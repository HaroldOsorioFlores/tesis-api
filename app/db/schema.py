import asyncio
from db_connection import create_connection

async def create_tables():
    try:
        connection = await create_connection()
        cursor = await connection.cursor()

        # Tabla de usuarios
        create_usuarios_table = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombres VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            correo VARCHAR(255) NOT NULL UNIQUE,
            dni VARCHAR(15) UNIQUE,
            f_nacimiento DATE,
            genero INT,
            contrasenia VARCHAR(255) NOT NULL,
            estado INT DEFAULT 1,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        await cursor.execute(create_usuarios_table)

        # Tabla de productos
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
        await cursor.execute(create_productos_table)

        # Tabla de recomendaciones
        create_recomendaciones_table = """
        CREATE TABLE IF NOT EXISTS recomendaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            peso DOUBLE,
            talla DOUBLE,
            edad INT,
            genero INT,
            act_fisica INT,
            estado INT DEFAULT 1,
            f_recomendacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
        """
        await cursor.execute(create_recomendaciones_table)

        # Tabla intermedia recomendacion_producto
        create_recomendacion_producto_table = """
        CREATE TABLE IF NOT EXISTS recomendacion_producto (
            id INT AUTO_INCREMENT PRIMARY KEY,
            recomendacion_id INT,
            producto_ids JSON,  -- Almacenar una lista de IDs de productos como JSON
            FOREIGN KEY (recomendacion_id) REFERENCES recomendaciones(id) ON DELETE CASCADE
        );
        """
        await cursor.execute(create_recomendacion_producto_table)

        await connection.commit()
        print("Tablas creadas exitosamente.")

    except Exception as error:  
        print("Error al crear las tablas:", error)
    
    finally:
        if cursor:
            await cursor.close()
        if connection:
            connection.close()

asyncio.run(create_tables())