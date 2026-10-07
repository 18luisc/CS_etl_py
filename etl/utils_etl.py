from sqlalchemy import Engine, text

def new_data(conne: Engine) -> bool:
    """
    Verifica si existen datos nuevos para cargar.
    """

    query_saved = text("""
        SELECT saved
        FROM hecho_atencion
        ORDER BY saved DESC
        LIMIT 1;
    """)

    query_fecha = text("""
        SELECT date
        FROM dim_fecha
        WHERE key_dim_fecha = (
            SELECT key_fecha_atencion
            FROM hecho_atencion
            ORDER BY key_fecha_atencion DESC
            LIMIT 1
        );
    """)

    with conne.connect() as con:
        try:
            rs_saved = con.execute(query_saved).fetchone()
            rs_fecha = con.execute(query_fecha).fetchone()

            # Primera carga
            if rs_saved is None or rs_fecha is None:
                return True

            lastupdate = rs_saved[0]
            lastdate = rs_fecha[0]

            # Convertir a fecha si vienen como datetime
            if hasattr(lastupdate, "date"):
                lastupdate = lastupdate.date()

            if hasattr(lastdate, "date"):
                lastdate = lastdate.date()

            if lastdate > lastupdate:
                return True

            print(
                f"No hay datos nuevos desde la última fecha de carga: {lastupdate}"
            )
            return False

        except Exception as e:
            print("[*] Error en new_data():", e)
            return False