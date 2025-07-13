import mysql.connector
import pytest
from task_manager import pripojeni_db

# pomocné funkce
def vloz_testovaci_ukol(conn, nazev="Test úkol", popis="Test popis"):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ukoly (nazev, popis)
        VALUES (%s, %s)
    """, (nazev, popis))
    conn.commit()
    return cursor.lastrowid

@pytest.fixture
def test_conn():
    conn = pripojeni_db(test_db=True)
    yield conn
    # úklid
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    cursor.close()
    conn.close()

def test_pridat_ukol_ok(test_conn):
    cursor = test_conn.cursor()
    cursor.execute("""
        INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)
    """, ("Test", "Test popis"))
    test_conn.commit()
    cursor.execute("SELECT * FROM ukoly WHERE nazev=%s", ("Test",))
    vysledek = cursor.fetchone()
    assert vysledek is not None
    cursor.close()

def test_pridat_ukol_fail(test_conn):
    cursor = test_conn.cursor()
    with pytest.raises(mysql.connector.errors.IntegrityError):
        cursor.execute("""
            INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)
        """, (None, None))  # povinné
    cursor.close()

def test_aktualizovat_ukol_ok(test_conn):
    id = vloz_testovaci_ukol(test_conn)
    cursor = test_conn.cursor()
    cursor.execute("""
        UPDATE ukoly SET stav='hotovo' WHERE id=%s
    """, (id,))
    test_conn.commit()
    cursor.execute("SELECT stav FROM ukoly WHERE id=%s", (id,))
    stav = cursor.fetchone()[0]
    assert stav == 'hotovo'
    cursor.close()

def test_aktualizovat_ukol_fail(test_conn):
    cursor = test_conn.cursor()
    cursor.execute("""
        UPDATE ukoly SET stav='hotovo' WHERE id=%s
    """, (99999,))  # neexistuje
    test_conn.commit()
    cursor.execute("SELECT * FROM ukoly WHERE id=%s", (99999,))
    assert cursor.fetchone() is None
    cursor.close()

def test_odstranit_ukol_ok(test_conn):
    id = vloz_testovaci_ukol(test_conn)
    cursor = test_conn.cursor()
    cursor.execute("DELETE FROM ukoly WHERE id=%s", (id,))
    test_conn.commit()
    cursor.execute("SELECT * FROM ukoly WHERE id=%s", (id,))
    assert cursor.fetchone() is None
    cursor.close()

def test_odstranit_ukol_fail(test_conn):
    cursor = test_conn.cursor()
    cursor.execute("DELETE FROM ukoly WHERE id=%s", (99999,))
    test_conn.commit()
    cursor.execute("SELECT * FROM ukoly WHERE id=%s", (99999,))
    assert cursor.fetchone() is None
    cursor.close()
