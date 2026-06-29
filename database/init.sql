USE ts_unamba;

-- ─────────────────────────────────────────
-- TABLAS BASE (sin dependencias)
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS CATEGORIA_DOCENTE (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    codigo    VARCHAR(20)  NOT NULL UNIQUE,
    nombre    VARCHAR(100) NOT NULL,
    modalidad ENUM('TIEMPO_COMPLETO', 'TIEMPO_PARCIAL') NOT NULL
);

CREATE TABLE IF NOT EXISTS CONDICION_LABORAL (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    codigo      VARCHAR(30)  NOT NULL UNIQUE,
    nombre      VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS RESOLUCION (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    numero_resolucion VARCHAR(100) NOT NULL,
    fecha_emision     DATE         NOT NULL,
    tipo              VARCHAR(100),
    descripcion       TEXT,
    emitida_por       VARCHAR(150),
    archivo_pdf       VARCHAR(255),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS USUARIO (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario  VARCHAR(100) NOT NULL UNIQUE,
    email           VARCHAR(150) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    rol             ENUM('ADMINISTRADOR', 'CONSULTOR') NOT NULL DEFAULT 'CONSULTOR',
    activo          TINYINT(1) DEFAULT 1,
    ultimo_acceso   DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- TABLAS CON DEPENDENCIAS
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS DOCENTE (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    nombres          VARCHAR(150) NOT NULL,
    apellidos        VARCHAR(150) NOT NULL,
    dni              VARCHAR(8)   NOT NULL UNIQUE,
    email            VARCHAR(150),
    fecha_nacimiento DATE,
    activo           TINYINT(1) DEFAULT 1,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS DOCENTE_RESOLUCION (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    docente_id   INT NOT NULL,
    resolucion_id INT NOT NULL,
    FOREIGN KEY (docente_id)    REFERENCES DOCENTE(id)    ON DELETE CASCADE,
    FOREIGN KEY (resolucion_id) REFERENCES RESOLUCION(id) ON DELETE CASCADE,
    UNIQUE KEY uq_docente_resolucion (docente_id, resolucion_id)
);

CREATE TABLE IF NOT EXISTS PERIODO_SERVICIO (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    docente_id      INT          NOT NULL,
    categoria_id    INT          NOT NULL,
    condicion_id    INT          NOT NULL,
    resolucion_id   INT,
    tipo_registro   ENUM('ACTIVO', 'CON_FECHAS', 'MANUAL') NOT NULL,
    etiqueta_periodo VARCHAR(100),
    anio_periodo    INT,
    fecha_inicio    DATE,
    fecha_fin       DATE,
    anios_brutos    INT          DEFAULT 0,
    meses_brutos    INT          DEFAULT 0,
    dias_brutos     INT          DEFAULT 0,
    activo          TINYINT(1)   DEFAULT 1,
    observaciones   TEXT,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (docente_id)   REFERENCES DOCENTE(id)           ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES CATEGORIA_DOCENTE(id) ON DELETE RESTRICT,
    FOREIGN KEY (condicion_id) REFERENCES CONDICION_LABORAL(id) ON DELETE RESTRICT,
    FOREIGN KEY (resolucion_id) REFERENCES RESOLUCION(id)       ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS DESCUENTO_PERIODO (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    periodo_id           INT NOT NULL UNIQUE,
    faltas_injustificadas INT DEFAULT 0,
    permisos_sin_goce    INT DEFAULT 0,
    licencias_sin_goce   INT DEFAULT 0,
    total_dias_descuento INT DEFAULT 0,
    observaciones        TEXT,
    FOREIGN KEY (periodo_id) REFERENCES PERIODO_SERVICIO(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CALCULO_TIEMPO_SERVICIO (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    docente_id           INT          NOT NULL,
    fecha_calculo        DATETIME     DEFAULT CURRENT_TIMESTAMP,
    total_anios          INT          DEFAULT 0,
    total_meses          INT          DEFAULT 0,
    total_dias           INT          DEFAULT 0,
    total_dias_brutos    INT          DEFAULT 0,
    total_dias_descuento INT          DEFAULT 0,
    total_dias_efectivos INT          DEFAULT 0,
    generado_por         VARCHAR(100),
    estado               ENUM('VIGENTE', 'HISTORICO') DEFAULT 'VIGENTE',
    FOREIGN KEY (docente_id) REFERENCES DOCENTE(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS DETALLE_CALCULO (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    calculo_id           INT NOT NULL,
    periodo_id           INT NOT NULL,
    dias_brutos_periodo  INT DEFAULT 0,
    dias_descuento_periodo INT DEFAULT 0,
    dias_efectivos_periodo INT DEFAULT 0,
    anios_efectivos      INT DEFAULT 0,
    meses_efectivos      INT DEFAULT 0,
    dias_efectivos       INT DEFAULT 0,
    FOREIGN KEY (calculo_id) REFERENCES CALCULO_TIEMPO_SERVICIO(id) ON DELETE CASCADE,
    FOREIGN KEY (periodo_id) REFERENCES PERIODO_SERVICIO(id)        ON DELETE CASCADE
);

-- ─────────────────────────────────────────
-- DATOS INICIALES
-- ─────────────────────────────────────────

INSERT INTO CATEGORIA_DOCENTE (codigo, nombre, modalidad) VALUES
('PA-TC',    'Principal - Tiempo Completo',              'TIEMPO_COMPLETO'),
('PA-TP20',  'Principal - Tiempo Parcial 20h',           'TIEMPO_PARCIAL'),
('PAs-TC',   'Asociado - Tiempo Completo',               'TIEMPO_COMPLETO'),
('PAs-TP20', 'Asociado - Tiempo Parcial 20h',            'TIEMPO_PARCIAL'),
('PPr-TC',   'Auxiliar - Tiempo Completo',               'TIEMPO_COMPLETO'),
('PPr-TP20', 'Auxiliar - Tiempo Parcial 20h',            'TIEMPO_PARCIAL'),
('DCB1',     'Contratado Banda 1 - Tiempo Completo',     'TIEMPO_COMPLETO'),
('DCB2',     'Contratado Banda 2 - Tiempo Parcial',      'TIEMPO_PARCIAL'),
('DCB3',     'Contratado Banda 3 - Tiempo Parcial',      'TIEMPO_PARCIAL');

INSERT INTO CONDICION_LABORAL (codigo, nombre, descripcion) VALUES
('CONTRATADO',  'Contratado',  'Docente bajo contrato temporal'),
('NOMBRADO',    'Nombrado',    'Docente con plaza permanente'),
('PROMOVIDO',   'Promovido',   'Docente promovido de categoría'),
('RATIFICADO',  'Ratificado',  'Docente ratificado en su plaza');

-- Contraseña por defecto: Admin123! (cámbiala tras el primer login)
INSERT INTO USUARIO (nombre_usuario, email, password_hash, rol) VALUES
('admin', 'admin@unamba.edu.pe', '$2b$12$placeholder_reemplazar_con_hash_real', 'ADMINISTRADOR');