import mysql.connector
from mysql.connector import Error

def pripojeni_db(test_db=False):
    try:
        db_name = "spravce_ukolu_test" if test_db else "spravce_ukolu"
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="xxxx",  # uprav dle svého hesla
            database=db_name
        )
        return conn
    except Error as e:
        print(f"Chyba při připojení k DB: {e}")
        return None

def vytvoreni_tabulky():
    conn = pripojeni_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav ENUM('nezahájeno', 'probíhá', 'hotovo') DEFAULT 'nezahájeno',
                datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

def pridat_ukol():
    nazev = input("Zadejte název úkolu: ").strip()
    popis = input("Zadejte popis úkolu: ").strip()
    if not nazev or not popis:
        print("Název i popis jsou povinné!")
        return
    conn = pripojeni_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ukoly (nazev, popis)
            VALUES (%s, %s)
        """, (nazev, popis))
        conn.commit()
        print("Úkol přidán.")
        cursor.close()
        conn.close()

def zobrazit_ukoly():
    conn = pripojeni_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nazev, popis, stav
            FROM ukoly
            WHERE stav IN ('nezahájeno', 'probíhá')
        """)
        vysledky = cursor.fetchall()
        if not vysledky:
            print("Žádné úkoly k zobrazení.")
        else:
            for u in vysledky:
                print(f"{u['id']}: {u['nazev']} - {u['popis']} ({u['stav']})")
        cursor.close()
        conn.close()

def aktualizovat_ukol():
    zobrazit_ukoly()
    try:
        id_ukolu = int(input("Zadejte ID úkolu pro aktualizaci: "))
    except ValueError:
        print("Neplatné ID.")
        return
    novy_stav = input("Zadejte nový stav (probíhá/hotovo): ").strip().lower()
    if novy_stav not in ("probíhá", "hotovo"):
        print("Neplatný stav!")
        return
    conn = pripojeni_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ukoly WHERE id=%s", (id_ukolu,))
        if not cursor.fetchone():
            print("Úkol s tímto ID neexistuje.")
        else:
            cursor.execute("""
                UPDATE ukoly SET stav=%s WHERE id=%s
            """, (novy_stav, id_ukolu))
            conn.commit()
            print("Stav úkolu aktualizován.")
        cursor.close()
        conn.close()

def odstranit_ukol():
    zobrazit_ukoly()
    try:
        id_ukolu = int(input("Zadejte ID úkolu pro smazání: "))
    except ValueError:
        print("Neplatné ID.")
        return
    conn = pripojeni_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ukoly WHERE id=%s", (id_ukolu,))
        if not cursor.fetchone():
            print("Úkol s tímto ID neexistuje.")
        else:
            cursor.execute("DELETE FROM ukoly WHERE id=%s", (id_ukolu,))
            conn.commit()
            print("Úkol smazán.")
        cursor.close()
        conn.close()

def hlavni_menu():
    while True:
        print("\n1. Přidat úkol\n2. Zobrazit úkoly\n3. Aktualizovat úkol\n4. Odstranit úkol\n5. Konec")
        volba = input("Vyberte možnost: ")
        if volba == "1":
            pridat_ukol()
        elif volba == "2":
            zobrazit_ukoly()
        elif volba == "3":
            aktualizovat_ukol()
        elif volba == "4":
            odstranit_ukol()
        elif volba == "5":
            print("Ukončuji program.")
            break
        else:
            print("Neplatná volba, zkuste to znovu.")

if __name__ == "__main__":
    vytvoreni_tabulky()
    hlavni_menu()
