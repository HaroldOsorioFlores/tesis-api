provider "aws" {
  region = "us-west-1"  # Cambia a la región que prefieras
}

# Crea un par de claves de AWS usando la clave pública generada
resource "aws_key_pair" "mi_llave" {
  key_name   = "mi_llave_terraform"  # Nombre para el par de claves en AWS
  public_key = file("C:/Users/gonza/.ssh/clave_aws.pub")  # Ruta a tu clave pública
}

# Crea un grupo de seguridad para permitir el acceso por SSH
resource "aws_security_group" "mi_grupo_seguridad" {
  name        = "mi_grupo_seguridad"
  description = "Grupo de seguridad para permitir SSH"

  # Permitir acceso al puerto 22 (SSH) desde cualquier IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Permite el acceso desde cualquier dirección IP (puedes restringirlo si lo deseas)
  }

  # Permitir tráfico de salida
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Permite todo el tráfico de salida
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Crea la instancia EC2
resource "aws_instance" "mi_instancia" {
  ami           = "ami-0da424eb883458071"  
  instance_type = "t2.micro"

  # Asocia la clave con la instancia EC2
  key_name = aws_key_pair.mi_llave.key_name

  # Asocia el grupo de seguridad a la instancia
  vpc_security_group_ids = [aws_security_group.mi_grupo_seguridad.id]

  tags = {
    Name = "MiInstancia"
  }
}
