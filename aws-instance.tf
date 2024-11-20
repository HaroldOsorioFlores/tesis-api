provider "aws" {
  region = "us-west-1"  
}

variable "public_key_path" {
  description = "Ruta a la clave pública SSH"
  type        = string
}

variable "db_password" {
  description = "Contraseña de la base de datos"
  type        = string
  sensitive   = true
}

resource "aws_key_pair" "recfoodcato_key" {
  key_name   = "recfoodcato_key"  
  public_key = file(var.public_key_path)  
}

resource "aws_security_group" "recfoodcato_security_group" {
  name        = "recfoodcato_security_group"
  description = "Grupo de seguridad para permitir SSH y acceso a la base de datos"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Limitar a direcciones IP específicas en producción
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Limitar a direcciones IP específicas en producción
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "recfoodcato_instance" {
  ami           = "ami-0da424eb883458071"  
  instance_type = "t2.micro"

  key_name = aws_key_pair.recfoodcato_key.key_name

  root_block_device {
    volume_size = 20  # Tamaño del volumen en GB
    volume_type = "gp3"  # Cambia a gp3
  }

  vpc_security_group_ids = [aws_security_group.recfoodcato_security_group.id]

  tags = {
    Name = "RecFoodCatoInstance"
  }
}

# Configuración de Amazon RDS
resource "aws_db_instance" "recfoodcato_db" {
  identifier           = "recfoodcato-db"
  allocated_storage    = 10
  db_name              = "recfoodcato_db"
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t3.micro"
  username             = "admin"
  password             = var.db_password  # Usa la variable para la contraseña
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
  publicly_accessible  = true  # Hacer la base de datos accesible públicamente

  vpc_security_group_ids = [aws_security_group.recfoodcato_security_group.id]

  tags = {
    Name = "RecFoodCatoInstanceDB"
  }
}