from db_connection import create_connection

def create_tables():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        create_usuarios_table = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombres VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            peso DOUBLE,
            talla DOUBLE,
            sexo VARCHAR(10),
            correo VARCHAR(255) NOT NULL UNIQUE,
            dni VARCHAR(15) UNIQUE,
            f_nacimiento DATE,
            contrasenia VARCHAR(255) NOT NULL,
            estado INT DEFAULT 1,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_usuarios_table)

        create_productos_table = """
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            proteinas DOUBLE,
            grasas DOUBLE,
            carbohidratos DOUBLE,
            estado INT DEFAULT 1,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_productos_table)

        create_recomendaciones_table = """
        CREATE TABLE IF NOT EXISTS recomendaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            producto_id INT,
            estado INT DEFAULT 1,
            f_recomendacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_recomendaciones_table)

        connection.commit()
        print("Tablas creadas exitosamente.")

    except Exception as error:  
        print("Error al crear las tablas:", error)
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

create_tables()
