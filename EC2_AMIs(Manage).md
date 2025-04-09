# AWS (EC2) AMIs MANAGEMENT

## 🧰 Instalación AWS CLI
1. Instala AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
2. Configura tus credenciales:
   ```bash
   aws configure
   ```
   Ingresá tu `Access Key`, `Secret Key`, `región`, y formato de salida (`json` recomendado).

---

## 🛠 Creación de una AMI (Imagen de la instancia EC2)
1. **Desactiva la protección contra detención** (si está activada):
   ```bash
   aws ec2 modify-instance-attribute --instance-id i-xxxxxxx --no-disable-api-stop
   ```

2. **Detén la instancia**:
   ```bash
   aws ec2 stop-instances --instance-ids i-xxxxxxx
   ```

3. **Crea una imagen (AMI)**:
   ```bash
   aws ec2 create-image --instance-id i-xxxxxxx --name "Nombre_AMI" --description "Backup de instancia"
   ```
   Esto generará una AMI y su snapshot asociado.

4. **Verifica el estado de la AMI**:
   ```bash
   aws ec2 describe-images --owners self
   ```

### 💸 Costos
- Las AMIs en sí no generan costos.
- **El snapshot asociado SÍ**, a razón de ~0.05 USD/GB/mes.
- Las instancias o volúmenes creados desde AMI también generan costos por uso.

---

## 💾 Crear y descargar una imagen del sistema manualmente (backup local)

1. Dentro de la instancia EC2:
   ```bash
   sudo dd if=/dev/xvda of=/home/ubuntu/backup.img bs=1M
   ```

2. Crea un bucket en S3:
   ```bash
   aws s3 mb s3://nombre-de-tu-bucket
   ```

3. Sube el archivo:
   ```bash
   aws s3 cp /home/ubuntu/backup.img s3://nombre-de-tu-bucket/
   ```
   *(Este comando se ejecuta dentro de la instancia EC2 donde generaste el archivo)*

4. Descarga el archivo a tu PC:
   ```bash
   aws s3 cp s3://nombre-de-tu-bucket/backup.img ./
   ```

---

## ☁️ Subir imagen de sistema a EC2 (desde backup local)

1. Convierte el archivo `.img` a `.vmdk` o `.raw` con herramientas como `qemu-img`.
2. Sube a S3:
   ```bash
   aws s3 cp backup.raw s3://tu-bucket/
   ```
3. Crea el rol necesario para VM Import:
   Ver guía oficial: https://docs.aws.amazon.com/vm-import/latest/userguide/vmimport-image-import.html

4. Importa la imagen:
   ```bash
   aws ec2 import-image --description "VM importada" --disk-containers Format=RAW,UserBucket={S3Bucket=tu-bucket,S3Key=backup.raw}
   ```
5. Una vez convertida en AMI, podés lanzar la instancia:
   ```bash
   aws ec2 run-instances --image-id ami-xxxxxxxx --instance-type t2.micro --key-name tu-par-claves
   ```

---

## 📨 Exportar una instancia EC2 como imagen OVA (para correr localmente)

1. Detené la instancia EC2:
   ```bash
   aws ec2 stop-instances --instance-ids i-xxxxxxx
   ```

2. Exportá la imagen:
   ```bash
   aws ec2 create-instance-export-task \
     --instance-id i-xxxxxxx \
     --target-environment vmware \
     --export-to-s3-task DiskImageFormat=OVA,ContainerFormat=ova,S3Bucket=tu-bucket,S3Prefix=exported/
   ```

3. Descargá el archivo OVA desde tu bucket S3:
   ```bash
   aws s3 cp s3://tu-bucket/exported/archivo.ova ./
   ```

4. Importalo en VirtualBox > Archivo > Importar Servicio Virtualizado

---

## ⬆️ Exportar una VM (VirtualBox) a EC2

1. Exportá desde VirtualBox como `.ova`
2. Convertí el archivo a `.raw` con `qemu-img`:
   ```bash
   qemu-img convert -O raw archivo.ova archivo.raw
   ```
3. Sube a S3:
   ```bash
   aws s3 cp archivo.raw s3://tu-bucket/
   ```
4. Importá la imagen:
   ```bash
   aws ec2 import-image --description "Import OVA" --disk-containers Format=RAW,UserBucket={S3Bucket=tu-bucket,S3Key=archivo.raw}
   ```

5. Esperá a que el AMI esté listo, y lanzá tu instancia desde él:
   ```bash
   aws ec2 run-instances --image-id ami-xxxxxxxx --instance-type t2.micro --key-name tu-clave
   ```

