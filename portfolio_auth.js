(function (global) {
    'use strict';

    const DB_NAME = 'market-scanner-portfolio-auth';
    const DB_VERSION = 1;
    const STORE_NAME = 'records';
    const DEVICE_KEY_ID = 'portfolio-device-key-v1';
    const SESSION_ID = 'portfolio-session-v1';
    const RECORD_VERSION = 1;
    const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000;

    function isSupported() {
        return Boolean(
            global.indexedDB &&
            global.crypto &&
            global.crypto.subtle &&
            global.TextEncoder &&
            global.TextDecoder
        );
    }

    function openDatabase() {
        return new Promise(function (resolve, reject) {
            const request = global.indexedDB.open(DB_NAME, DB_VERSION);
            request.onupgradeneeded = function () {
                const database = request.result;
                if (!database.objectStoreNames.contains(STORE_NAME)) {
                    database.createObjectStore(STORE_NAME, { keyPath: 'id' });
                }
            };
            request.onsuccess = function () {
                resolve(request.result);
            };
            request.onerror = function () {
                reject(request.error || new Error('IndexedDB indisponibil'));
            };
            request.onblocked = function () {
                reject(new Error('Baza locală de autentificare este blocată'));
            };
        });
    }

    async function readRecord(id) {
        const database = await openDatabase();
        try {
            return await new Promise(function (resolve, reject) {
                const transaction = database.transaction(STORE_NAME, 'readonly');
                const request = transaction.objectStore(STORE_NAME).get(id);
                request.onsuccess = function () {
                    resolve(request.result || null);
                };
                request.onerror = function () {
                    reject(request.error || new Error('Citirea sesiunii a eșuat'));
                };
                transaction.onabort = function () {
                    reject(transaction.error || new Error('Citirea sesiunii a fost anulată'));
                };
            });
        } finally {
            database.close();
        }
    }

    async function writeRecord(record) {
        const database = await openDatabase();
        try {
            await new Promise(function (resolve, reject) {
                const transaction = database.transaction(STORE_NAME, 'readwrite');
                transaction.objectStore(STORE_NAME).put(record);
                transaction.oncomplete = function () {
                    resolve();
                };
                transaction.onerror = function () {
                    reject(transaction.error || new Error('Salvarea sesiunii a eșuat'));
                };
                transaction.onabort = function () {
                    reject(transaction.error || new Error('Salvarea sesiunii a fost anulată'));
                };
            });
        } finally {
            database.close();
        }
    }

    async function deleteRecords(ids) {
        const database = await openDatabase();
        try {
            await new Promise(function (resolve, reject) {
                const transaction = database.transaction(STORE_NAME, 'readwrite');
                const store = transaction.objectStore(STORE_NAME);
                ids.forEach(function (id) {
                    store.delete(id);
                });
                transaction.oncomplete = function () {
                    resolve();
                };
                transaction.onerror = function () {
                    reject(transaction.error || new Error('Ștergerea sesiunii a eșuat'));
                };
                transaction.onabort = function () {
                    reject(transaction.error || new Error('Ștergerea sesiunii a fost anulată'));
                };
            });
        } finally {
            database.close();
        }
    }

    function bytesToBase64(value) {
        const bytes = new Uint8Array(value);
        let binary = '';
        bytes.forEach(function (byte) {
            binary += String.fromCharCode(byte);
        });
        return global.btoa(binary);
    }

    function base64ToBytes(value) {
        const binary = global.atob(value);
        const bytes = new Uint8Array(binary.length);
        for (let index = 0; index < binary.length; index += 1) {
            bytes[index] = binary.charCodeAt(index);
        }
        return bytes;
    }

    function additionalData() {
        const origin = global.location && global.location.origin
            ? global.location.origin
            : 'local';
        return new global.TextEncoder().encode(
            'market-scanner-portfolio-auth-v1|' + origin
        );
    }

    async function getOrCreateDeviceKey() {
        const existing = await readRecord(DEVICE_KEY_ID);
        if (existing && existing.key) {
            return existing.key;
        }
        const key = await global.crypto.subtle.generateKey(
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
        await writeRecord({
            id: DEVICE_KEY_ID,
            version: RECORD_VERSION,
            key: key,
            createdAt: Date.now(),
        });
        return key;
    }

    async function clearCredential() {
        if (!isSupported()) {
            return;
        }
        try {
            await deleteRecords([SESSION_ID, DEVICE_KEY_ID]);
        } catch (error) {
            console.warn('Sesiunea locală nu a putut fi ștearsă.', error);
        }
    }

    async function rememberCredential(credential) {
        if (!isSupported() || typeof credential !== 'string' || !credential) {
            return false;
        }
        try {
            const key = await getOrCreateDeviceKey();
            const iv = global.crypto.getRandomValues(new Uint8Array(12));
            const encrypted = await global.crypto.subtle.encrypt(
                {
                    name: 'AES-GCM',
                    iv: iv,
                    additionalData: additionalData(),
                },
                key,
                new global.TextEncoder().encode(credential)
            );
            const now = Date.now();
            await writeRecord({
                id: SESSION_ID,
                version: RECORD_VERSION,
                iv: bytesToBase64(iv),
                ciphertext: bytesToBase64(encrypted),
                createdAt: now,
                expiresAt: now + SESSION_TTL_MS,
            });
            return true;
        } catch (error) {
            console.warn(
                'Autentificarea rămâne activă doar în pagina curentă; ' +
                'memorarea locală nu este disponibilă.',
                error
            );
            return false;
        }
    }

    async function restoreCredential() {
        if (!isSupported()) {
            return null;
        }
        try {
            const session = await readRecord(SESSION_ID);
            if (
                !session ||
                session.version !== RECORD_VERSION ||
                !Number.isFinite(session.expiresAt) ||
                session.expiresAt <= Date.now()
            ) {
                if (session) {
                    await clearCredential();
                }
                return null;
            }
            const keyRecord = await readRecord(DEVICE_KEY_ID);
            if (!keyRecord || !keyRecord.key) {
                await clearCredential();
                return null;
            }
            const decrypted = await global.crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: base64ToBytes(session.iv),
                    additionalData: additionalData(),
                },
                keyRecord.key,
                base64ToBytes(session.ciphertext)
            );
            return new global.TextDecoder().decode(decrypted);
        } catch (error) {
            await clearCredential();
            console.warn('Sesiunea locală nu mai este validă.', error);
            return null;
        }
    }

    global.PortfolioAuthPersistence = Object.freeze({
        sessionTtlMs: SESSION_TTL_MS,
        isSupported: isSupported,
        rememberCredential: rememberCredential,
        restoreCredential: restoreCredential,
        clearCredential: clearCredential,
    });
}(window));
