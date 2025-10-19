from typing import List, Optional, Dict, Union, Set
import asyncio, os, time
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, constant_time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib

from KeyisBTools.cryptography.sign import s2          # как у тебя
from KeyisBTools.cryptography import m1               # как у тебя

from ._app import GNRequest
from gnobjects.net.objects import Url
from KeyisBTools.cryptography.bytes import hash3

# ----- Fast helpers -----
import random
from typing import List, Optional, Dict, Union, Set, Deque, Tuple
from collections import deque


class _FastSession:
    __slots__ = ("ekey", "kmac", "aad_dom", "nonce_hi", "nonce_lo", "last_init_ts")

    def __init__(self, ekey: bytes, kmac: bytes, aad_dom: bytes):
        self.ekey = ekey      # 32b AES key
        self.kmac = kmac      # 32b BLAKE2s MAC key
        self.aad_dom = aad_dom  # 64b domain_hash + 1b version
        r = os.urandom(12)
        self.nonce_hi = int.from_bytes(r[:4], "big")
        self.nonce_lo = int.from_bytes(r[4:], "big")
        self.last_init_ts = int(time.time())

    def next_nonce(self) -> bytes:
        self.nonce_lo = (self.nonce_lo + 1) & ((1 << 64) - 1)
        if self.nonce_lo == 0:
            self.nonce_hi = (self.nonce_hi + 1) & ((1 << 32) - 1)
        return self.nonce_hi.to_bytes(4, "big") + self.nonce_lo.to_bytes(8, "big")


def _hkdf32(key_material: bytes, info: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=info).derive(key_material)

def _aesctr_xor(key32: bytes, nonce12: bytes, data: bytes) -> bytes:
    # 12b -> 16b IV (дополняем нулями), быстрый поток на CPU с AES-NI
    cipher = Cipher(algorithms.AES(key32), modes.CTR(nonce12 + b"\x00\x00\x00\x00"))
    enc = cipher.encryptor()
    return enc.update(data) + enc.finalize()

def _blake2s_tag(key32: bytes, parts: list[bytes], size: int = 16) -> bytes:
    b = hashlib.blake2s(digest_size=size, key=key32)
    for p in parts: b.update(p)
    return b.digest()

_FAST_INIT = 0xA1
_FAST_DATA = 0xA0
_FAST_REKEY = 0xA2

_MAX_KEY_LIFETIME = 600  # 10 мин


class KDCObject:
    """
    Две схемы:
      Stable (legacy, для доменов из set_stable_domains): h(8)|sig(164)|dom_h(64)|m1.encrypt(...)
      Fast (по умолчанию для остальных):
        init: h(8)|0xA1|sig(164)|dom_h(64)|nonce(12)|CT|tag(16)
        data: h(8)|0xA0|dom_h(64)|nonce(12)|CT|tag(16)
    """
    def __init__(self, domain: str, kdc_domain: str, kdc_key: bytes,
                 requested_domains: List[str], active_key_synchronization: bool = True):
        self._domain = domain
        self._domain_hash = hash3(domain.encode())
        self._kdc_domain = kdc_domain
        self._kdc_key = kdc_key
        self._requested_domains = requested_domains
        self._active_key_synchronization = active_key_synchronization

        from ._client import AsyncClient
        self._client = AsyncClient(domain)
        self._client.setKDC(self)

        self._servers_keys = {}
        self._servers_keys_hash_domain = {}
        self._servers_keys_domain_hash = {}

        self._stable_domains = set()
        self._domains_b_cache = {}

        # теперь fast хранит несколько версий ключей
        # domain -> deque[(version, FastSession, ts)]
        self._fast_sessions: Dict[str, Deque[Tuple[int, _FastSession, int]]] = {}


        # настройки rekey
        self._fast_rekey_default = 1000
        self._fast_rekey_chances: dict[str, int] = {}

        self._fast_version_counter = 0

    # ---- API управления стабильными доменами ----
    def set_stable_domains(self, domains: List[str]) -> None:
        self._stable_domains = set(domains)

    def add_stable_domain(self, domain: str) -> None:
        self._stable_domains.add(domain)

    # ---- Инициализация/обновление KDC ----
    async def init(self, servers_keys: Optional[Dict[str, bytes]] = None,
                   requested_domains: Optional[List[str]] = None): # type: ignore
        if requested_domains is not None:
            self._requested_domains += requested_domains

        if servers_keys is not None:
            for i in list(self._requested_domains):
                if i in servers_keys:
                    self._requested_domains.remove(i)
        else:
            servers_keys = {}

        self._servers_keys.update(servers_keys)

        if len(self._requested_domains) > 0:
            await self.requestKDC(self._requested_domains) # type: ignore
        else:
            self._update()

    def _update(self):
        for d in self._servers_keys.keys():
            h = hash3(d.encode())
            self._servers_keys_hash_domain[h] = d
            self._servers_keys_domain_hash[d] = h

    async def requestKDC(self, domain_or_hash: Union[str, bytes, List[Union[str, bytes]]]):
        if self._kdc_domain not in self._servers_keys:
            self._servers_keys[self._kdc_domain] = self._kdc_key
            h = hash3(self._kdc_domain.encode())
            self._servers_keys_hash_domain[h] = self._kdc_domain
            self._servers_keys_domain_hash[self._kdc_domain] = h

        if not isinstance(domain_or_hash, list):
            domain_or_hash = [domain_or_hash]

        r = await self._client.request(GNRequest('GET', Url(f'gn://{self._kdc_domain}/api/sys/server/keys'),
                                                payload=domain_or_hash))
        if not r.command.ok:
            print(f'ERROR: {r.command} {r.payload}')
            raise r

        self._servers_keys.update(r.payload)
        self._update()

    # ---- Вспомогалки ----
    def _db(self, domain: str) -> bytes:
        b = self._domains_b_cache.get(domain)
        if b is None:
            b = domain.encode('utf-8', 'strict')
            self._domains_b_cache[domain] = b
        return b

    def _get_or_create_fast_session(self, domain: str, key: bytes, sig: Optional[bytes]) -> _FastSession:
        dq = self._fast_sessions.get(domain)
        if dq and len(dq) > 0:
            return dq[-1][1]  # (version, session, ts)

        # Сессии ещё нет — только создаём (НЕ добавляем!)
        info_enc = b"GN-fast|enc"
        info_mac = b"GN-fast|mac"
        if sig is not None:
            info_enc += b"|sig:" + sig[:32]
            info_mac += b"|sig:" + sig[-32:]

        ekey = _hkdf32(key, info_enc)   # 32b
        kmac = _hkdf32(key, info_mac)   # 32b
        aad_dom = self._servers_keys_domain_hash[domain] + bytes([1])  # 64b + версия fast

        return _FastSession(ekey, kmac, aad_dom)



    # ---- Legacy путь (для стабильных доменов) ----
    async def _encode_legacy(self, domain: str, request: bytes) -> bytes:
        key = self._servers_keys[domain]
        sig = await asyncio.to_thread(s2.sign, key)
        payload = memoryview(request)[8:]
        data = await asyncio.to_thread(m1.encrypt, self._db(domain), sig, payload, key)
        return request[:8] + sig + self._servers_keys_domain_hash[domain] + data

    async def _decode_legacy(self, response: bytes):
        r = response
        if len(r) < 8+164+64:
            return r, None
        h = r[:8]
        body = memoryview(r)[8:]
        sig = bytes(body[:164])
        dom_h = bytes(body[164:164+64])
        data = bytes(body[164+64:])

        if dom_h not in self._servers_keys_hash_domain:
            if not self._active_key_synchronization:
                return r, None
            await self.requestKDC(dom_h)

        d = self._servers_keys_hash_domain[dom_h]
        key = self._servers_keys[d]
        ok = await asyncio.to_thread(s2.verify, key, sig)
        if not ok:
            return None, None

        pt = await asyncio.to_thread(m1.decrypt, self._db(self._domain), sig, data, key)
        return h + pt, d



    # ---- Публичные методы ----
    async def encode(self, domain: str, request: bytes):
        if domain not in self._servers_keys:
            if not self._active_key_synchronization:
                return request
            await self.requestKDC(domain)

        if domain in self._stable_domains:
            return await self._encode_legacy(domain, request)
        else:
            return await self._encode_fast(domain, request)

    async def decode(self, response: bytes):
        if len(response) >= 9 and response[8] in (_FAST_INIT, _FAST_DATA, _FAST_REKEY):
            res = await self._decode_fast(response)
            if res != (response, None):
                return res
        return await self._decode_legacy(response)




    def set_rekey_chance(self, domain: str, chance: int):
        """Установить шанс rekey 1/chance для конкретного домена."""
        self._fast_rekey_chances[domain] = chance

    def _get_rekey_chance(self, domain: str) -> int:
        return self._fast_rekey_chances.get(domain, self._fast_rekey_default)

    def _get_latest_session(self, domain: str) -> tuple[Optional[int], Optional[_FastSession]]:
        dq = self._fast_sessions.get(domain)
        if dq and len(dq) > 0:
            return dq[-1][0], dq[-1][1]
        return None, None


    def _add_new_session(self, domain: str, session: _FastSession):
        version = self._fast_version_counter
        self._fast_version_counter += 1
        dq = self._fast_sessions.setdefault(domain, deque())
        dq.append((version, session, int(time.time())))
        # чистим старые ключи
        while dq and (int(time.time()) - dq[0][2]) > _MAX_KEY_LIFETIME:
            dq.popleft()
        return version

    def _get_session_by_version(self, domain: str, version: int) -> _FastSession | None:
        dq = self._fast_sessions.get(domain)
        if not dq: return None
        for v, s, ts in reversed(dq):
            if v == version:
                return s
        return None

    def _should_rekey(self, domain: str) -> bool:
        chance = self._get_rekey_chance(domain)
        return random.randint(1, chance) == 1

    # ---------------- FAST ENCODE ----------------
    async def _encode_fast(self, domain: str, request: bytes) -> bytes:
        key = self._servers_keys[domain]
        h = request[:8]
        payload = memoryview(request)[8:]
        dom_h = self._servers_keys_domain_hash[domain]

        # --- если нет ни одной сессии — это init ---
        version, fs = self._get_latest_session(domain)
        if fs is None:
            sig = await asyncio.to_thread(s2.sign, key)
            fs = self._get_or_create_fast_session(domain, key, sig)
            version = self._add_new_session(domain, fs)   # добавляем ТУТ (единственный раз)
            nonce = fs.next_nonce()
            ct = _aesctr_xor(fs.ekey, nonce, payload)
            tag = _blake2s_tag(fs.kmac, [h, bytes([_FAST_INIT]), sig, dom_h, nonce, version.to_bytes(4,'big'), ct], 16)
            return h + bytes([_FAST_INIT]) + sig + dom_h + nonce + version.to_bytes(4,'big') + ct + tag

        # --- обычный пакет или rekey ---
        if self._should_rekey(domain):
            sig = await asyncio.to_thread(s2.sign, key)
            new_fs = self._get_or_create_fast_session(domain, key, sig)
            new_ver = self._add_new_session(domain, new_fs)  # добавили новую версию
            nonce = new_fs.next_nonce()
            ct = _aesctr_xor(new_fs.ekey, nonce, payload)
            tag = _blake2s_tag(new_fs.kmac, [h, bytes([_FAST_REKEY]), sig, dom_h, nonce, new_ver.to_bytes(4,'big'), ct], 16)
            return h + bytes([_FAST_REKEY]) + sig + dom_h + nonce + new_ver.to_bytes(4,'big') + ct + tag
        else:
            nonce = fs.next_nonce()
            ct = _aesctr_xor(fs.ekey, nonce, payload)
            tag = _blake2s_tag(fs.kmac, [h, bytes([_FAST_DATA]), dom_h, nonce, version.to_bytes(4,'big'), ct], 16)
            return h + bytes([_FAST_DATA]) + dom_h + nonce + version.to_bytes(4,'big') + ct + tag

    # ---------------- FAST DECODE ----------------
    async def _decode_fast(self, response: bytes):
        # общий нижний предел для DATA: h(8)+flag(1)+dom_h(64)+nonce(12)+ver(4)+tag(16)
        if len(response) < 8+1+64+12+4+16:
            return response, None

        h = response[:8]
        flag = response[8]
        p = 9

        if flag == _FAST_INIT or flag == _FAST_REKEY:
            # для INIT/REKEY нужен sig(164)
            if len(response) < 8+1+164+64+12+4+16:
                return response, None
            sig = response[p:p+164]; p += 164
            dom_h = response[p:p+64]; p += 64
            nonce = response[p:p+12]; p += 12
            version = int.from_bytes(response[p:p+4], 'big'); p += 4
            ct = response[p:-16]
            tag = response[-16:]

            if dom_h not in self._servers_keys_hash_domain:
                if not self._active_key_synchronization:
                    return response, None
                await self.requestKDC(dom_h)

            d = self._servers_keys_hash_domain[dom_h]
            key = self._servers_keys[d]

            ok = await asyncio.to_thread(s2.verify, key, sig)
            if not ok:
                return None, None

            new_fs = self._get_or_create_fast_session(d, key, sig)
            # фиксируем новую версию ключа (важно!): версия с пакета — authoritative
            # если версия уже есть (редкий гоночный случай) — просто используем существующую
            existing = self._get_session_by_version(d, version)
            fs_to_use = existing if existing is not None else new_fs
            if existing is None:
                # зарегистрировать именно с номером version из пакета:
                dq = self._fast_sessions.setdefault(d, deque())
                dq.append((version, new_fs, int(time.time())))
                # почистить старые
                while dq and (int(time.time()) - dq[0][2]) > _MAX_KEY_LIFETIME:
                    dq.popleft()

            calc = _blake2s_tag(fs_to_use.kmac, [h, bytes([flag]), sig, dom_h, nonce, version.to_bytes(4,'big'), ct], 16)
            if not constant_time.bytes_eq(calc, tag):
                return None, None

            pt = _aesctr_xor(fs_to_use.ekey, nonce, ct)
            return h + pt, d

        elif flag == _FAST_DATA:
            dom_h = response[p:p+64]; p += 64
            nonce = response[p:p+12]; p += 12
            version = int.from_bytes(response[p:p+4], 'big'); p += 4
            ct = response[p:-16]
            tag = response[-16:]

            if dom_h not in self._servers_keys_hash_domain:
                if not self._active_key_synchronization:
                    return response, None
                await self.requestKDC(dom_h)

            d = self._servers_keys_hash_domain[dom_h]
            fs = self._get_session_by_version(d, version)
            if fs is None:
                return None, None

            calc = _blake2s_tag(fs.kmac, [h, bytes([_FAST_DATA]), dom_h, nonce, version.to_bytes(4,'big'), ct], 16)
            if not constant_time.bytes_eq(calc, tag):
                return None, None

            pt = _aesctr_xor(fs.ekey, nonce, ct)
            return h + pt, d

        return response, None
