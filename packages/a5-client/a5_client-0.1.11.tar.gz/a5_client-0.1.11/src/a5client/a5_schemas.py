schemas = {
    "components":{
        "schemas": {
            "Modelo": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "identificador único del modelo"
                    },
                    "nombre": {
                        "type": "string",
                        "description": "Nombre del modelo"
                    },
                    "tipo": {
                        "type": "string",
                        "description": "Tipo de modelo"
                    }
                }
            },
            "ArrayOfModelos": {
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Modelo"
                }
            },
            "Calibrado": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único del calibrado"
                    },
                    "model_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único del modelo"
                    },
                    "nombre": {
                        "type": "string",
                        "description": "nombre del calibrado",
                        "format": "regexp"
                    },
                    "activar": {
                        "type": "boolean",
                        "description": "activar el calibrado",
                        "default": True
                    },
                    "outputs": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Output"
                        },
                        "description": "Series de salida del calibrado"
                    },
                    "parametros": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Parametro"
                        },
                        "description": "Parámetros del calibrado"
                    },
                    "estados_iniciales": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Estado"
                        },
                        "description": "Estados iniciales del calibrado"
                    },
                    "forzantes": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Forzante"
                        },
                        "description": "Series de entrada del calibrado"
                    },
                    "selected": {
                        "type": "boolean",
                        "description": "Si el calibrado debe seleccionarse como el principal para las series de salida",
                        "defaultValue": False
                    },
                    "out_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "id de estación de salida del calibrado"
                    },
                    "area_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "id de area del calibrado"
                    },
                    "tramo_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "id de tramo de curso de agua del calibrado"
                    },
                    "dt": {
                        "$ref": "#/components/schemas/TimeInterval",
                        "description": "intervalo temporal del calibrado en formato SQL, p. ej '1 days' o '12 hours' o '00:30:00'",
                        "defaultValue": "1 days"
                    },
                    "t_offset": {
                        "$ref": "#/components/schemas/TimeInterval",
                        "description": "offset temporal del modelo en formato SQL, p ej '9 hours'",
                        "defaultValue": "9 hours"
                    },
                    "grupo_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "id de grupo de calibrados"
                    }
                },
                "required": [
                    "model_id",
                    "nombre"
                ],
                "table_name" : "calibrados"
            },
            "TimeInterval": {
                "oneOf": [
                    {
                        "type": "string",
                        "format": "time-interval"
                    },
                    {
                        "type": "object",
                        "properties": {
                            "milliseconds": {
                                "type": "integer",
                                "format": "int64"
                            },
                            "seconds": {
                                "type": "integer",
                                "format": "int64"
                            },
                            "minutes": {
                                "type": "integer",
                                "format": "int64"
                            },
                            "hours": {
                                "type": "integer",
                                "format": "int64"
                            },
                            "days": {
                                "type": "integer",
                                "format": "int64"
                            },
                            "months": {
                                "type": "integer",
                                "format": "int64"
                            },
                            "years": {
                                "type": "integer",
                                "format": "int64"
                            }
                        }
                    }
                ]
            },
            "Output": {
                "type": "object",
                "properties": {
                    "series_table": {
                        "type": "string",
                        "description": "tabla a la que pertenece la serie de salida",
                        "enum": [
                            "series",
                            "series_areal"
                        ],
                        "defaultValue": "series"
                    },
                    "series_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de la serie de salida"
                    },
                    "orden": {
                        "type": "integer",
                        "format": "int64",
                        "description": "número de orden de salida",
                        "minimum": 1
                    },
                    "cal_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de calibrado",
                        "readOnly": True
                    },
                    "id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único",
                        "readOnly": True
                    }
                },
                "required": [
                    "series_id",
                    "orden"
                ],
                "table_name": "cal_out"
            },
            "Parametro": {
                "type": "object",
                "properties": {
                    "valor": {
                        "type": "number",
                        "format": "float",
                        "description": "valor del parámetro"
                    },
                    "orden": {
                        "type": "integer",
                        "format": "int64",
                        "description": "número de orden del parámetro",
                        "minimum": 1
                    },
                    "cal_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de calibrado",
                        "readOnly": True
                    },
                    "id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único",
                        "readOnly": True
                    }
                },
                "required": [
                    "valor",
                    "orden"
                ],
                "table_name": "cal_pars"
            },
            "Estado": {
                "type": "object",
                "properties": {
                    "valor": {
                        "type": "number",
                        "format": "float",
                        "description": "valor del estado"
                    },
                    "orden": {
                        "type": "integer",
                        "format": "int64",
                        "description": "número de orden del estado",
                        "minimum": 1
                    },
                    "cal_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de calibrado",
                        "readOnly": True
                    },
                    "id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único",
                        "readOnly": True
                    }
                },
                "required": [
                    "valor",
                    "orden"
                ],
                "table_name": "cal_estados"
            },
            "Forzante": {
                "type": "object",
                "properties": {
                    "series_table": {
                        "type": "string",
                        "description": "tabla a la que pertenece la serie de entrada",
                        "enum": [
                            "series",
                            "series_areal"
                        ],
                        "defaultValue": "series"
                    },
                    "series_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de la serie de entrada"
                    },
                    "orden": {
                        "type": "integer",
                        "format": "int64",
                        "description": "número de orden de entrada",
                        "minimum": 1
                    },
                    "cal_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de calibrado",
                        "readOnly": True
                    },
                    "id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único",
                        "readOnly": True
                    },
                    "model_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de modelo",
                        "readOnly": True
                    },
                    "serie": {
                        "$ref":"#/components/schemas/Serie",
                        "description": "serie: objeto Serie",
                        "foreign_key": "series_id"
                    }
                },
                "required": [
                    "series_id",
                    "orden"
                ],
                "table_name": "forzantes"
            },
            "Corrida": {
                "type": "object",
                "properties": {
                    "forecast_date": {
                        "type": "string",
                        "description": "Fecha de emisión"
                    },
                    "series": {
                        "type": "array",
                        "description": "series temporales simuladas",
                        "items": {
                            "$ref": "#/components/schemas/SerieTemporalSim"
                        }
                    }
                },
                "required": [
                    "forecast_date",
                    "series"
                ]
            },
            "SerieTemporalSim": {
                "type": "object",
                "properties": {
                    "series_table": {
                        "type": "string",
                        "description": "tabla de la serie simulada",
                        "enum": [
                            "series",
                            "series_areal"
                        ],
                        "defaultValue": "series"
                    },
                    "series_id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "identificador único de serie simulada"
                    },
                    "pronosticos": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Pronostico"
                        },
                        "description": "Tuplas de la serie simulada"
                    }
                },
                "required": [
                    "series_table",
                    "series_id",
                    "pronosticos"
                ]
            },
            "Pronostico": {
                "type": "object",
                "properties": {
                    "timestart": {
                        "type": "string",
                        "description": "fecha-hora inicial del pronóstico",
                        "format": "date-time",
                        "interval": "begin"
                    },
                    "timeend": {
                        "type": "string",
                        "description": "fecha-hora final del pronóstico",
                        "format": "date-time",
                        "interval": "end"
                    },
                    "valor": {
                        "type": "number",
                        "format": "float",
                        "description": "valor del pronóstico"
                    },
                    "qualifier": {
                        "type": "string",
                        "description": "calificador opcional para diferenciar subseries, default:'main'",
                        "defaultValue": "main"
                    }
                },
                "required": [
                    "timestart",
                    "timeend",
                    "valor"
                ]
            },
            "Observacion": {
                "type": "object",
                "properties": {
                    "tipo": {
                        "type": "string",
                        "description": "tipo de registro",
                        "enum": [
                            "areal",
                            "puntual",
                            "raster"
                        ]
                    },
                    "timestart": {
                        "type": "string",
                        "description": "fecha-hora inicial del registro"
                    },
                    "timeend": {
                        "type": "string",
                        "description": "fecha-hora final del registro"
                    },
                    "valor": {
                        "oneOf": [
                            {
                                "type": "number",
                                "format": "float"
                            },
                            {
                                "type": "string",
                                "format": "binary"
                            }
                        ],
                        "description": "valor del registro"
                    },
                    "series_id": {
                        "type": "integer",
                        "description": "id de serie"
                    }
                },
                "required": ["timestart", "valor"]
            },
            "Accessor": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "nombre identificador del recurso"
                    },
                    "url": {
                        "type": "string",
                        "description": "ubicación del recurso"
                    },
                    "class": {
                        "type": "string",
                        "description": "tipo de recurso"
                    },
                    "series_tipo": {
                        "type": "string",
                        "enum": [
                            "puntual",
                            "areal",
                            "raster"
                        ],
                        "description": "tipo de la serie temporal correspondiente al recurso"
                    },
                    "series_source_id": {
                        "type": "integer",
                        "description": "id de la fuente correspondiente al recurso"
                    },
                    "time_update": {
                        "type": "string",
                        "description": "última fecha de actualización del recurso"
                    },
                    "config": {
                        "type": "object",
                        "properties": {
                            "download_dir": {
                                "type": "string",
                                "description": "directorio de descargas"
                            },
                            "tmp_dir": {
                                "type": "string",
                                "description": "directorio temporal"
                            },
                            "tables_dir": {
                                "type": "string",
                                "description": "directorio de tablas"
                            },
                            "host": {
                                "type": "string",
                                "description": "IP o url del recurso"
                            },
                            "user": {
                                "type": "string",
                                "description": "nombre de usuario del recurso"
                            },
                            "password": {
                                "type": "string",
                                "description": "contraseña del recurso"
                            },
                            "path": {
                                "type": "string",
                                "description": "ruta del recurso"
                            }
                        }
                    },
                    "series_id": {
                        "type": "integer",
                        "description": "id de la serie temporal correspondiente al recurso"
                    }
                }
            },
            "Fuente": {
                "oneOf": [ 
                    {"$ref": "#/components/schemas/FuenteRaster"},
                    {"$ref": "#/components/schemas/FuentePuntual"}
                ]
            },
            "FuenteRaster": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "id de la fuente"
                    },
                    "nombre": {
                        "type": "string",
                        "description": "nombre de la fuente"
                    },
                    "data_table": {
                        "type": "string",
                        "description": ""
                    },
                    "data_column": {
                        "type": "string",
                        "description": ""
                    },
                    "tipo": {
                        "type": "string",
                        "description": "tipo de la fuente"
                    },
                    "def_proc_id": {
                        "type": "string",
                        "description": "id de procedimiento por defecto de la fuente"
                    },
                    "def_dt": {
                        "type": "string",
                        "description": "intervalo temporal por defecto de la fuente"
                    },
                    "hora_corte": {
                        "type": "string",
                        "description": "hora de corte por defecto de la fuente"
                    },
                    "def_unit_id": {
                        "type": "integer",
                        "description": "id de unidades por defecto de la fuente"
                    },
                    "def_var_id": {
                        "type": "integer",
                        "description": "id de variable por defecto de la fuente"
                    },
                    "fd_column": {
                        "type": "string",
                        "description": ""
                    },
                    "mad_table": {
                        "type": "string",
                        "description": ""
                    },
                    "scale_factor": {
                        "type": "number",
                        "description": "factor de escala por defecto de la fuente"
                    },
                    "data_offset": {
                        "type": "number",
                        "description": "offset por defecto de la fuente"
                    },
                    "def_pixel_height": {
                        "type": " number",
                        "description": "altura de pixel por defecto de la fuente"
                    },
                    "def_pixel_width": {
                        "type": "number",
                        "description": "ancho de pixel por defecto de la fuente"
                    },
                    "def_srid": {
                        "type": "integer",
                        "description": "código SRID de georeferenciación por defecto de la fuente"
                    },
                    "def_extent": {
                        "type": "string",
                        "description": "id de procedimiento por defecto de la fuente"
                    },
                    "date_column": {
                        "type": "string",
                        "description": ""
                    },
                    "def_pixel_type": {
                        "type": "string",
                        "description": "tipo de dato del pixel por defecto de la fuente"
                    },
                    "abstract": {
                        "type": "string",
                        "description": "descripción de la fuente"
                    },
                    "source": {
                        "type": "string",
                        "description": "ubicación del origen de la fuente"
                    }
                }
            },
            "FuentePuntual": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "id numérico de la fuente"
                    },
                    "tabla_id": {
                        "type": "string",
                        "description": "id alfanumérico de la fuente"
                    },
                    "nombre": {
                        "type": "string",
                        "description": "nombre de la fuente"
                    },
                    "public": {
                        "type": "boolean",
                        "description": "si la fuente es pública"
                    },
                    "public_his_plata": {
                        "type": "boolean",
                        "description": "si la fuente está disponible para HIS-Plata"
                    }
                }
            },
            "Variable": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "id de la variable"
                    },
                    "var": {
                        "description": "código alfanumérico de la variable",
                        "type": "string"
                    },
                    "nombre": {
                        "description": "Nombre de la variable",
                        "type": "string"
                    },
                    "abrev": {
                        "description": "Abreviatura de la variable",
                        "type": "string"
                    },
                    "type": {
                        "description": "tipo de la variable",
                        "type": "string"
                    },
                    "dataType": {
                        "description": "tipo de dato de la variable según ODM",
                        "type": "string"
                    },
                    "valueType": {
                        "description": "tipo de valor de la variable según ODM",
                        "type": "string"
                    },
                    "GeneralCategory": {
                        "description": "categoría general de la variable según ODM",
                        "type": "string"
                    },
                    "VariableName": {
                        "description": "nombre de la variable según ODM",
                        "type": "string"
                    },
                    "SampleMedium": {
                        "description": "Medio de muestreo según ODM",
                        "type": "string"
                    },
                    "def_unit_id": {
                        "description": "id de unidades por defecto",
                        "type": "integer"
                    },
                    "timeSupport": {
                        "description": "soporte temporal de la medición",
                        "type": "string"
                    }
                }
            },
            "Procedimiento": {
                "type": "object",
                "properties": {
                    "id": {
                        "description": "id del Procedimiento",
                        "type": "integer"
                    },
                    "nombre": {
                        "description": "Nombre del Procedimiento",
                        "type": "string"
                    },
                    "abrev": {
                        "description": "Nombre abreviado del Procedimiento",
                        "type": "string"
                    },
                    "descripicion": {
                        "description": "descripción del Procedimiento",
                        "type": "string"
                    }
                }
            },
            "Unidad": {
                "type": "object",
                "properties": {
                    "id": {
                        "description": "id de la Unidad",
                        "type": "integer"
                    },
                    "nombre": {
                        "description": "Nombre de la Unidad",
                        "type": "string"
                    },
                    "abrev": {
                        "description": "Nombre abreviado de la Unidad",
                        "type": "string"
                    },
                    "UnitsID": {
                        "description": "ID de unidades según ODM",
                        "type": "string"
                    },
                    "UnitsType": {
                        "description": "tipo de unidades según ODM",
                        "type": "string"
                    }
                }
            },
            "Estacion": {
                "type": "object",
                "properties": {
                    "fuentes_id": {
                        "description": "id de la fuente",
                        "type": "integer"
                    },
                    "nombre": {
                        "description": "nombre de la estación (parcial o completo)",
                        "type": "string"
                    },
                    "unid": {
                        "description": "identificador único de la estación",
                        "type": "integer"
                    },
                    "id": {
                        "description": "identificador de la estación dentro de la fuente (red) a la que pertenece",
                        "type": "integer"
                    },
                    "id_externo": {
                        "description": "id externo de la estación",
                        "type": "string"
                    },
                    "distrito": {
                        "description": "jurisdicción de segundo orden en la que se encuentra la estación (parcial o completa)",
                        "type": "string"
                    },
                    "pais": {
                        "description": "jurisdicción de primer orden en la que se encuentra la estación (parcial o completa)",
                        "type": "string"
                    },
                    "has_obs": {
                        "description": "si la estación posee registros observados",
                        "type": "boolean"
                    },
                    "real": {
                        "name": "real",
                        "type": "boolean"
                    },
                    "habilitar": {
                        "description": "si la estación se encuentra habilitada",
                        "type": "boolean"
                    },
                    "tipo": {
                        "description": "tipo de la estación",
                        "type": "string"
                    },
                    "has_prono": {
                        "description": "si la estación posee registros pronosticados",
                        "type": "boolean"
                    },
                    "rio": {
                        "description": "curso de agua de la estación (parcial o completo)",
                        "type": "string"
                    },
                    "tipo_2": {
                        "description": "tipo de estación: marca y/o modelo",
                        "type": "string"
                    },
                    "geom": {
                        "description": "coordenadas geográficas de la estación",
                        "$ref": "#/components/schemas/Geometry"
                    },
                    "propietario": {
                        "description": "propietario de la estación (nombre parcial o completo)",
                        "type": "string"
                    },
                    "automatica": {
                        "description": "si la estación es automática",
                        "type": "boolean"
                    },
                    "ubicacion": {
                        "description": "ubicación de la estación",
                        "type": "string"
                    },
                    "localidad": {
                        "description": "localidad en la que se encuentra la estación",
                        "type": "string"
                    },
                    "tabla": {
                        "description": "identificación alfanumérica de la fuente (red) a la que pertenece la estación",
                        "type": "string"
                    }
                }
            },
            "Area": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "description": "nombre del área",
                        "type": "string"
                    },
                    "id": {
                        "description": "identificador único del área",
                        "type": "integer"
                    },
                    "geom": {
                        "description": "geometría del área (polígono)",
                        "$ref": "#/components/schemas/Geometry"
                    },
                    "exutorio": {
                        "description": "geometría de la sección de salida (punto)",
                        "$ref": "#/components/schemas/Geometry"
                    }
                }
            },
            "Escena": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "description": "nombre de la escena",
                        "type": "string"
                    },
                    "unid": {
                        "description": "identificador único de la escena",
                        "type": "integer"
                    },
                    "geom": {
                        "description": "geometría de la escena (polígono)",
                        "$ref": "#/components/schemas/Geometry"
                    }
                }
            },
            "Geometry": {
                "type": "object",
                "properties": {
                    "type": {
                        "description": "tipo de geometría",
                        "type": "string",
                        "enum": [ "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon", "GeometryCollection" ]
                    },
                    "coordinates": {
                        "description": "coordenadas",
                        "oneOf": [
                            {
                                "$ref": "#/components/schemas/Position"
                            },
                            {
                                "$ref": "#/components/schemas/LineString"
                            },
                            {
                                "$ref": "#/components/schemas/Polygon"
                            },
                            {
                                "$ref": "#/components/schemas/MultiPolygon"
                            }
                        ]
                    }
                },
                "required": [ "type", "coordinates"]
            },
        "Position": {
                "type": "array",
                "items": {
                    "type": "number"
                },
                "minItems": 2,
                "maxItems": 3
            },
            "LineString": {
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Position"
                },
                "minItems": 2
            },
            "Polygon": {
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/LineString"
                }
            },
            "MultiPolygon": {
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Polygon"
                }
            },
            "Serie": {
                "type": "object",
                "properties": {
                    "tipo": {
                        "description": "tipo de observación",
                        "type": "string",
                        "enum": [ "puntual", "areal", "raster" ]
                    },
                    "id": {
                        "description": "id de la serie",
                        "type": "integer"
                    },
                    "estacion": {
                        "description": "estación/área/escena (para tipo: puntual/areal/raster respectivamente)",
                        "oneOf": [
                            {
                                "$ref": "#/components/schemas/Estacion"
                            },
                            {
                                "$ref": "#/components/schemas/Area"
                            },
                            {
                                "$ref": "#/components/schemas/Escena"
                            }
                        ],
                        "foreign_key": "estacion_id"
                    },
                    "var": {
                        "description": "variable",
                        "$ref": "#/components/schemas/Variable"
                    },
                    "procedimiento": {
                        "description": "procedimiento",
                        "$ref": "#/components/schemas/Procedimiento",
                        "foreign_key": "proc_id"
                    },
                    "unidades": {
                        "description": "unidades",
                        "$ref": "#/components/schemas/Unidad",
                        "foreign_key": "unit_id"
                    },
                    "fuente": {
                        "description": "fuente (para tipo: areal/raster)",
                        "$ref": "#/components/schemas/Fuente",
                        "foreign_key": "fuentes_id"
                    },
                    "observaciones": {
                        "description": "arreglo de observaciones correspondientes a la serie",
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Observacion"
                        }
                    }
                },
                "required": [ "tipo", "estacion_id", "var_id", "proc_id", "unit_id"],
                "table_name" : "series"
            },
            "ObservacionDia": {
                "type": "object",
                "properties": {
                    "date": {
                        "description": "fecha de la observación",
                        "type": "string"
                    },
                    "series_id": {
                        "description": "id de serie",
                        "type": "integer"
                    },
                    "var_id": {
                        "description": "id de variable",
                        "type": "integer"
                    },
                    "proc_id": {
                        "description": "id de procedimiento",
                        "type": "integer"
                    },
                    "unit_id": {
                        "description": "id de unidades",
                        "type": "integer"
                    },
                    "estacion_id": {
                        "description": "id de estacion (tipo puntual)",
                        "type": "integer"
                    },
                    "valor": {
                        "description": "valor de la observación",
                        "type": "number"
                    }, 
                    "fuentes_id": {
                        "description": "id de fuente (tipo areal y raster)",
                        "type": "integer"
                    },
                    "area_id":  {
                        "description": "id de area (tipo areal)",
                        "type": "integer"
                    },
                    "tipo": {
                        "description": "tipo de observación",
                        "type": "string",
                        "enum": ["puntual", "areal", "raster"]
                    },
                    "doy": {
                        "description": "día del año",
                        "type": "integer"
                    },
                    "cume_dist": {
                        "description": "valor de distribución acumulada",
                        "type": "number"
                    }
                }
            },
            "Asociacion": {
                "type": "object",
                "properties": {
                    "id":{
                        "type": "integer"
                    },
                    "source_tipo":{
                        "type": "string"
                    },
                    "source_series_id":{
                        "type": "integer"
                    },
                    "dest_tipo":{
                        "type": "string"
                    },
                    "dest_series_id":{
                        "type": "integer"
                    },
                    "agg_func":{
                        "type": "string"
                    },
                    "dt":{
                        "type": "string"
                    },
                    "t_offset": {
                        "type": "string"
                    },
                    "precision":{
                        "type": "integer"
                    }, 
                    "source_time_support":{
                        "type": "string"
                    },
                    "source_is_inst":{
                        "type": "boolean"
                    },
                    "source_series": {
                        "$ref": "#/components/schemas/Serie"
                    },
                    "dest_series": {
                        "$ref": "#/components/schemas/Serie"
                    },
                    "site": {
                        "$ref": "#/components/schemas/Estacion"
                    },
                    "expresion": {
                        "type": "string"
                    }
                }
            },
            "EstadisticosDiarios": {
                "type": "object",
                "properties": {
                    "tipo":{
                        "description": "tipo de observación",
                        "type": "string"
                    },
                    "series_id":{
                        "description": "id de serie",
                        "type": "integer"
                    },
                    "doy":{
                        "description": "día del año",
                        "type": "integer"
                    },
                    "count":{
                        "description": "cantidad de registros",
                        "type": "integer"
                    },
                    "min":{
                        "description": "valor mínimo",
                        "type": "number"
                    },
                    "max":{
                        "description": "valor máximo",
                        "type": "number"
                    },
                    "mean":{
                        "description": "valor medio",
                        "type": "number"
                    },
                    "p01":{
                        "description": "percentil 1",
                        "type": "number"
                    },
                    "p10":{
                        "description": "percentil 10",
                        "type": "number"
                    },
                    "p50":{
                        "description": "percentil 50",
                        "type": "number"
                    },
                    "p90":{
                        "description": "percentil 90",
                        "type": "number"
                    },
                    "p99":{
                        "description": "percentil 99",
                        "type": "number"
                    },
                    "window_size":{
                        "description": "ventana temporal para el suavizado en días (a partir de y hasta el día del año en cuestión)",
                        "type": "integer"
                    },
                    "timestart":{
                        "description": "fecha inicial",
                        "type": "string"
                    },
                    "timeend":{
                        "description": "fecha final",
                        "type": "string"
                    }
                }
            },
            "Percentil": {
                "type": "object",
                "properties": {
                    "tipo":{
                        "type": "string"
                    },
                    "series_id":{
                        "type": "integer"
                    },
                    "cuantil":{
                        "type": "number"
                    },
                    "window_size":{
                        "type": "integer"
                    },
                    "doy":{
                        "type": "integer"
                    },
                    "timestart":{
                        "type": "string"
                    },
                    "timeend":{
                        "type": "string"
                    },
                    "count":{
                        "type": "integer"
                    },
                    "valor":{
                        "type": "number"
                    }
                }
            },
            "GeoJSON": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string"
                    },
                    "features": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Feature"
                        }
                    }
                }
            },
            "Feature": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "number"
                    },
                    "geometry": {
                        "$ref": "#/components/schemas/Geometry"
                    },
                    "properties": {
                        "type": "object"
                    }
                }
            }
        }
    }
}
