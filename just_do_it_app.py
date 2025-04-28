# -*- coding: utf-8 -*- 
"""
Auteur: hamza et soufian 
"""
import sys
import mysql.connector
from passlib.hash import pbkdf2_sha256 
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox,
    QListWidgetItem, QCheckBox, QProgressBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont,QIcon
 
# Classe pour gérer la base de données MySQL
class Database:
    def __init__(self):
        # Connexion à la base de données
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="h@mz@dine2006.",
            database="todo_app"
        )
        self.cursor = self.connection.cursor()  

    # Créer un nouvel utilisateur
    def create_user(self, username, password_hash):
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Erreur : {err}")
            return False

    # Récupérer un utilisateur en fonction du nom d'utilisateur
    def get_user(self, username):
        self.cursor.execute(
            "SELECT user_id, password_hash FROM users WHERE username = %s",
            (username,)
        )
        return self.cursor.fetchone()

    # Ajouter une tâche à l'utilisateur
    def add_task(self, user_id, task_text):
        self.cursor.execute(
            "INSERT INTO tasks (user_id, task_text) VALUES (%s, %s)",
            (user_id, task_text)
        )
        self.connection.commit()
        return self.cursor.lastrowid

    # Récupérer toutes les tâches d'un utilisateur
    def get_tasks(self, user_id):
        self.cursor.execute(
            "SELECT task_id, task_text, is_completed FROM tasks WHERE user_id = %s",
            (user_id,)
        )
        return self.cursor.fetchall()

    # Mettre à jour l'état de complétion d'une tâche
    def update_task_status(self, task_id, is_completed):
        self.cursor.execute(
            "UPDATE tasks SET is_completed = %s WHERE task_id = %s",
            (is_completed, task_id)
        )
        self.connection.commit()

    # Supprimer une tâche
    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
        self.connection.commit()

# Classe pour styliser les boutons
class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setFont(QFont("Arial", 15, QFont.Bold))
        self.setStyleSheet("""
            QPushButton {
                background-color: #6C63FF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5a52e8;
            }
            QPushButton:pressed {
                background-color: #4a44c1;
            }
        """)

# Classe pour la page de connexion
class LoginPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Connexion")
        self.setGeometry(700, 400, 500, 400)
        self.setWindowIcon(QIcon("to-do-list-logo.png"))
        self.setStyleSheet("background-color: #f0f0ff;")

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Just do it")
        title.setFont(QFont("Arial", 25, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c2c6c; margin-bottom: 30px;")
        layout.addWidget(title)

        input_style = """
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 25px;
                background-color: #ffffff;
            }
        """

        # Champ de saisie pour le nom d'utilisateur
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur...")
        self.username_input.setStyleSheet(input_style)
        layout.addWidget(self.username_input)

        # Champ de saisie pour le mot de passe
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(input_style)
        layout.addWidget(self.password_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Bouton de connexion
        self.login_button = StyledButton("Connexion")
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)

        # Bouton d'inscription
        self.register_button = StyledButton("Inscription")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5;
            }
            QPushButton:hover {
                background-color: #2c3e90;
            }
            QPushButton:pressed {
                background-color: #1c2b66;
            }
        """)
        self.register_button.clicked.connect(self.show_signup_page)
        buttons_layout.addWidget(self.register_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    # Fonction de gestion de la connexion
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer le nom d'utilisateur et le mot de passe")
            return

        user = self.db.get_user(username)
        if user and pbkdf2_sha256.verify(password, user[1]):
            self.user_id = user[0]
            self.close()
            self.todo_window = TodoWindow(self.db, self.user_id)
            self.todo_window.show()
        else:
            QMessageBox.warning(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect")

    # Fonction pour afficher la page d'inscription
    def show_signup_page(self):
        self.signup_page = SignupPage(self.db)
        self.signup_page.show()
        self.close()

# Classe pour la page d'inscription
class SignupPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Inscription")
        self.setGeometry(700, 400, 500, 400)
        self.setWindowIcon(QIcon("to-do-list-logo.png"))
        self.setStyleSheet("background-color: #f0f0ff;")

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Inscription")
        title.setFont(QFont("Arial", 25, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c2c6c; margin-bottom: 30px;")
        layout.addWidget(title)

        input_style = """
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 25px;
                background-color: #ffffff;
            }
        """

        # Champ de saisie pour le nom d'utilisateur
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur...")
        self.username_input.setStyleSheet(input_style)
        layout.addWidget(self.username_input)

        # Champ de saisie pour le mot de passe
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(input_style)
        layout.addWidget(self.password_input)

        # Champ de confirmation du mot de passe
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmer le mot de passe...")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet(input_style)
        layout.addWidget(self.confirm_password_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Bouton d'inscription
        self.signup_button = StyledButton("S'inscrire")
        self.signup_button.clicked.connect(self.handle_signup)
        buttons_layout.addWidget(self.signup_button)

        # Bouton de retour à la page de connexion
        self.back_button = StyledButton("Retour")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """)
        self.back_button.clicked.connect(self.show_login_page)
        buttons_layout.addWidget(self.back_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    # Fonction pour gérer l'inscription de l'utilisateur
    def handle_signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Erreur", "Le mot de passe doit contenir au moins 8 caractères")
            return

        password_hash = pbkdf2_sha256.hash(password)
        if self.db.create_user(username, password_hash):
            QMessageBox.information(self, "Succès", "Inscription réussie. Veuillez vous connecter.")
            self.show_login_page()
        else:
            QMessageBox.warning(self, "Erreur", "Nom d'utilisateur déjà existant")

    # Fonction pour revenir à la page de connexion
    def show_login_page(self):
        self.login_page = LoginPage(self.db)
        self.login_page.show()
        self.close()

# Classe pour la fenêtre des tâches
class TodoWindow(QMainWindow):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.setWindowTitle("Mes Tâches")
        self.setWindowIcon(QIcon("to-do-list-logo.png"))
        self.setGeometry(500, 300, 900, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f4fc;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #bbb;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        input_style = """
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 25px;
                background-color: #ffffff;
            }
        """

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("Mes Tâches")
        header.setFont(QFont("Arial", 25, QFont.Bold))
        header.setStyleSheet("color: #2c2c6c; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Layout pour ajouter une tâche
        add_task_layout = QHBoxLayout()
        add_task_layout.setSpacing(15)

        # Champ de saisie pour ajouter une tâche
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Ajouter une nouvelle tâche...")
        self.task_input.setMinimumHeight(50)
        self.task_input.setStyleSheet(input_style)
        add_task_layout.addWidget(self.task_input, 4)

        # Bouton pour ajouter la tâche
        self.add_button = StyledButton("Ajouter")
        self.add_button.setMinimumWidth(120)
        self.add_button.clicked.connect(self.add_task)
        add_task_layout.addWidget(self.add_button, 1)

        layout.addLayout(add_task_layout)

        # Liste des tâches
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget::item {
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #d0e6ff;
            }
        """)
        layout.addWidget(self.task_list)

        # Barre de progression des tâches
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #6C63FF;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.load_tasks()
        
        # Bouton de retour à la page de connexion
        self.retour_button = StyledButton("Retour")
        self.retour_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """)
        self.retour_button.setMinimumWidth(120)
        self.retour_button.clicked.connect(self.retour_login)
        layout.addWidget(self.retour_button)

        central_widget.setLayout(layout)

    # Ajouter une tâche à la liste
    def add_task(self):
        task_text = self.task_input.text().strip()
        if not task_text:
            return

        task_id = self.db.add_task(self.user_id, task_text)
        self.add_task_to_list(task_id, task_text, False)
        self.task_input.clear()

        self.update_progress_bar()

    # Charger les tâches de l'utilisateur
    def load_tasks(self):
        self.task_list.clear()
        tasks = self.db.get_tasks(self.user_id)
        for task_id, task_text, is_completed in tasks:
            self.add_task_to_list(task_id, task_text, is_completed)

        self.update_progress_bar()

    # Ajouter une tâche dans la liste affichée
    def add_task_to_list(self, task_id, task_text, is_completed):
        # Créer un QListWidgetItem (espace réservé dans la liste)
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 60)) # Définissez la hauteur personnalisée pour l'élément de liste
    
        # Créez le widget qui sera affiché dans le widget QListWidget
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
    
        # Disposition horizontale pour la case à cocher, l'étiquette et le bouton de suppression
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(15)
    
        # Case à cocher pour l'achèvement des tâches
        checkbox = QCheckBox()
        checkbox.setChecked(is_completed)
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #6C63FF;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #6C63FF;
            }
        """)
       # Connecter la case à cocher pour mettre à jour l'état des tâches dans la base de données
        checkbox.stateChanged.connect(
            lambda state, task_id=task_id: self.update_task_status(task_id, state == Qt.Checked)
        )
        layout.addWidget(checkbox)
    
        # Task label
        label = QLabel(task_text)
        label.setFont(QFont("Arial", 12))
        if is_completed:
            label.setStyleSheet("""
                QLabel {
                    color: #999;
                    text-decoration: line-through;
                    padding: 5px;
                }
            """)
        else:
            label.setStyleSheet("""
                QLabel {
                    color: #333;
                    padding: 5px;
                }
            """)
        layout.addWidget(label, 1)
    
        # suprimer button
        delete_button = QPushButton("X")
        delete_button.setFont(QFont("Arial", 12, QFont.Bold))
        delete_button.setStyleSheet("""
            QPushButton {
                color: #f44336;
                background-color: transparent;
                border: none;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #ffebee;
            }
        """)
        delete_button.clicked.connect(
            lambda _, task_id=task_id, item=item: self.delete_task(task_id, item)
        )
        layout.addWidget(delete_button)
    
        #Définir layout  sur le widget personnalisé
        widget.setLayout(layout)
    
      # Ajoutez l'élément au widget QListWidget et définissez son widget
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)
    

    # Mettre à jour l'état de la tâche (complète ou non)
    def update_task_status(self, task_id, is_completed):
        self.db.update_task_status(task_id, is_completed)
        self.update_progress_bar()

    # Supprimer une tâche de la liste
    
    def delete_task(self, task_id, item):
        reply = QMessageBox.question(
            self,                        # parent
            "Confirmation",              # title
            "Êtes-vous sûr de vouloir supprimer cette tâche ?",  # message
            QMessageBox.Yes | QMessageBox.No ,  # buttons
            QMessageBox.No               # default button
        )
    
        if reply == QMessageBox.Yes:
            self.db.delete_task(task_id)
            self.task_list.takeItem(self.task_list.row(item))
            self.update_progress_bar()

    # Mettre à jour la barre de progression
    def update_progress_bar(self):
        tasks = self.db.get_tasks(self.user_id)
        print(tasks)
        total_tasks = len(tasks)
        if total_tasks == 0:
            self.progress_bar.setValue(0)
        else:
            completed_tasks = sum(1 for task in tasks if task[2])
            self.progress_bar.setValue(int((completed_tasks / total_tasks) * 100))
    
    #retour a la page de conexion
    def retour_login(self):
        self.login_page = LoginPage(self.db)
        self.login_page.show()
        self.close()
        
  
    
  
    
  
  
def main():
    # Crée une instance de l'application PyQt5 avec les arguments de la ligne de commande
    app = QApplication(sys.argv)

    # Définit le style visuel de l'application (ici, le style "Fusion")
    app.setStyle("Fusion")

    # Crée une instance de la classe Database pour gérer les opérations sur la base de données
    db = Database()

    # Crée une instance de la page de connexion (LoginPage) en lui passant l'objet db
    # Cela permet à la page de connexion d'interagir avec la base de données pour vérifier les utilisateurs
    login_page = LoginPage(db)  # Remarquez que 'LoginWindow' a été changé en 'LoginPage' pour mieux refléter le rôle de cette classe

    # Affiche la page de connexion à l'écran
    login_page.show()

    # Exécute l'application PyQt5 et attend la fin de son exécution (blocage jusqu'à la fermeture de la fenêtre)
    sys.exit(app.exec_())

# Cette ligne exécute la fonction main uniquement si le script est exécuté directement
# Cela permet d'éviter que la fonction main ne soit appelée si ce fichier est importé dans un autre module
if __name__ == "__main__":
    main()
