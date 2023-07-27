import mysql.connector
from cryptography.fernet import Fernet
import hashlib
import base64
import getpass
import os
import contextlib

def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def load_key():
    try:
        with open("encryption_key.key", "rb") as key_file:
            key = key_file.read()
    except FileNotFoundError:
        key = generate_key("your_password")
        with open("encryption_key.key", "wb") as key_file:
            key_file.write(key)
    return key

class FernetEncryption:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data):
        f = Fernet(self.key)
        return f.encrypt(data.encode()).decode()

    def decrypt(self, data):
        f = Fernet(self.key)
        return f.decrypt(data.encode()).decode()

def get_mysql_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='Kriptografi'
    )

@contextlib.contextmanager
def mysql_connection():
    connection = get_mysql_connection()
    try:
        yield connection
    finally:
        connection.close()

def save_to_mysql(data):
    with mysql_connection() as connection:
        cursor = connection.cursor()
        insert_query = "INSERT INTO passwords (nama, username, password) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, data)
        connection.commit()

def get_from_mysql():
    with mysql_connection() as connection:
        cursor = connection.cursor()
        select_query = "SELECT id, nama, username, password FROM passwords"
        cursor.execute(select_query)
        data = cursor.fetchall()
    return data

def delete_record_by_id(record_id):
    with mysql_connection() as connection:
        cursor = connection.cursor()
        delete_query = "DELETE FROM passwords WHERE id = %s"
        cursor.execute(delete_query, (record_id,))
        connection.commit()

def show_login():
    os.system('clear')
    print("+----------------------------------------------------------------------+")
    print("|            PASSWORD MANAGER APP by KELOMPOK 3 KRIPTOGRAFI            |")
    print("+----------------------------------------------------------------------+")
    print("| Robby Akbar Abdullah    [2107421004]                                 |")
    print("| Shoffan Darul Mufti     [2107421009]                                 |")
    print("| Fajar Firdaus de Roock  [2107421014]                                 |")
    print("| Muhammad Daffa Rasyid   [2107421020]                                 |")
    print("| Berlianna Upik Nurniati [2107421022]                                 |")
    print("+----------------------------------------------------------------------+")
    print("| [1] LOGIN                                                            |")
    print("| [2] KELUAR                                                           |")
    print("+----------------------------------------------------------------------+")

def login(password):
    attempt = 3
    while attempt > 0:
        user_password = getpass.getpass("Masukkan password: ")
        if user_password == password:
            print("Login berhasil!")
            os.system('clear')
            return True
        else:
            attempt -= 1
            print(f"Password salah. Anda memiliki {attempt} kesempatan lagi.")
    print("Anda telah mencapai batas percobaan login. Aplikasi akan keluar.")
    exit(0)

def main():
    master_password = "1"  # Ganti dengan password utama Anda

    # Langkah 1: Muat kunci dari file
    key = load_key()
    fernet_encryptor = FernetEncryption(key)

    while True:
        show_login()
        choice = input("\nPilih menu [1/2]: ")

        if choice == "1":
            if login(master_password):
                while True:
                    # Langkah 4: Ambil data dari database MySQL
                    data_from_mysql = get_from_mysql()

                    # Langkah 5: Dekripsi setiap record di kolom password dengan Fernet
                    decrypted_data = [(id, name, user, fernet_encryptor.decrypt(pwd)) for id, name, user, pwd in data_from_mysql]

                    # Langkah 6: Tampilkan data di terminal
                    print("+----------------------------------------------------------------------+")
                    print("|            PASSWORD MANAGER APP by KELOMPOK 3 KRIPTOGRAFI            |")
                    print("+----------------------------------------------------------------------+")
                    print("|                           LIST PASSWORD                              |")
                    print("+----------------------------------------------------------------------+")
                    for id, name, user, pwd in decrypted_data:
                        print(f"  [{id}] {name}\t[user/pass: {user} / {pwd}]")

                    print("\n  MENU")
                    print("  [1] TAMBAH PASSWORD")
                    print("  [2] HAPUS PASSWORD ")
                    print("  [3] KELUAR         ")
                    option = input("\nPilih menu [1/2/3]: ")

                    if option == "1":
                        os.system('clear')
                        print("+----------------------------------------------------------------------+")
                        print("|            PASSWORD MANAGER APP by KELOMPOK 3 KRIPTOGRAFI            |")
                        print("+----------------------------------------------------------------------+")
                        print("|                          TAMBAH PASSWORD                             |")
                        print("+----------------------------------------------------------------------+")
                        # Input data dari pengguna
                        nama = input("Masukkan Nama (4-8 kata): ")
                        username = input("Masukkan Username: ")
                        password = input("Masukkan Password: ")

                        # Langkah 2: Enkripsi password dengan Fernet
                        encrypted_password = fernet_encryptor.encrypt(password)

                        # Langkah 3: Simpan data terenkripsi ke database MySQL
                        data_to_save = (nama, username, encrypted_password)
                        save_to_mysql(data_to_save)
                        os.system('clear')

                    elif option == "2":
                        # Langkah 7: Hapus record berdasarkan ID (contoh: hapus record dengan ID 1)
                        record_id_to_delete = input("Masukkan ID record yang akan dihapus: ")
                        delete_record_by_id(record_id_to_delete)
                        os.system('clear')
                    elif option == "3":
                        print("Terima kasih! Sampai jumpa lagi.")
                        break
                    else:
                        os.system('clear')
                        print("Pilihan tidak valid. Silakan pilih menu 1, 2, atau 3.")
            else:
                print("Login gagal. Akses ditolak!")
        elif choice == "2":
            print("Terima kasih! Sampai jumpa lagi.")
            break
        else:
            os.system('clear')
            print("Pilihan tidak valid. Silakan pilih menu 1 atau 2.")

if __name__ == "__main__":
    main()
