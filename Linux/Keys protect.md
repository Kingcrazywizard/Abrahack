Para crear una carpeta segura donde almacenar tus claves SSH e API keys, es recomendable
que utilices un sistema de cifrado o almacenes de secretos como `gpg` (GNU Privacy
Guard) o herramientas como `Keyring`. A continuación, te muestro cómo hacerlo utilizando
`gpg` para cifrar y descifrar archivos.

### Paso 1: Generar una clave pública y privada GPG

Primero, necesitas generar una clave pública/privada GPG si aún no la tienes. Abre un
terminal (por ejemplo, en Linux o macOS) e introduce los siguientes comandos:

```sh
gpg --full-generate-key
```

Siguientes las instrucciones de generación:
- Selecciona `RSA and RSA` como tipo de clave.
- Escribe una longitud adecuada para tu clave (por ejemplo, 4096 bits).
- Introduce un nombre y apellidos que identifiquen esta clave.
- Ingresa una contraseña segura para proteger tu clave privada.

### Paso 2: Crear la carpeta de almacenamiento

Crea una carpeta donde guardarás tus claves:

```sh
mkdir -p ~/.ssh/encrypted_keys
```

### Paso 3: Cifrar los archivos con `gpg`

Supongamos que tienes un archivo llamado `id_rsa` (tus claves SSH) y otro `api_key.txt`
(tus API keys). Los cifras utilizando tu clave GPG generada:

```sh
gpg --symmetric --cipher-algo AES256 ~/.ssh/id_rsa
gpg --symmetric --cipher-algo AES256 ~/.ssh/api_key.txt
```

Estos comandos crean archivos `id_rsa.gpg` y `api_key.txt.gpg`, respectivamente, que
están cifrados.

### Paso 4: Almacenar los archivos cifrados

Mueve los archivos cifrados a la carpeta que has creado:

```sh
mv ~/.ssh/id_rsa.gpg ~/.ssh/api_key.txt.gpg ~/.ssh/encrypted_keys/
```

Ahora tienes tus claves SSH e API keys en una carpeta segura.

### Paso 5: Descifrar y usar los archivos cuando sea necesario

Cuando quieras usar las claves, puedes descifrarlos temporalmente:

```sh
gpg --output ~/.ssh/id_rsa --decrypt ~/.ssh/encrypted_keys/id_rsa.gpg
```

Para que puedas usar `id_rsa` normalmente en un terminal actualizado, puedes usar:

```sh
eval $(ssh-agent) && ssh-add ~/.ssh/id_rsa
```


 