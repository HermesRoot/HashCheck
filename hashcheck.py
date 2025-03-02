import wx
import hashlib
import datetime
import os


class ChecksumVerifier(wx.Frame):
    def __init__(self, parent, title):
        super(ChecksumVerifier, self).__init__(parent, title=title, size=(500, 350))

        self.create_menu_bar()

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        # Espaçamento extra no topo
        vbox.AddSpacer(15)

        # Linha do arquivo
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(panel, label='Arquivo:'), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.file_path_ctrl = wx.TextCtrl(panel, style=wx.TE_READONLY)
        file_button = wx.Button(panel, label='Selecionar')
        file_button.Bind(wx.EVT_BUTTON, self.on_select_file)
        hbox1.Add(self.file_path_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        hbox1.Add(file_button, flag=wx.ALL, border=5)
        vbox.Add(hbox1, flag=wx.EXPAND)

        # Linha do algoritmo e hash esperado
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(panel, label='Algoritmo:'), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.algorithm_choice = wx.ComboBox(panel, choices=['md5', 'sha1', 'sha256', 'sha512'], style=wx.CB_READONLY)
        self.algorithm_choice.SetStringSelection('sha256')
        hbox2.Add(self.algorithm_choice, flag=wx.ALL, border=5)
        hbox2.Add(wx.StaticText(panel, label='Hash esperado:'), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.expected_hash_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.expected_hash_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_verify)
        hbox2.Add(self.expected_hash_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(hbox2, flag=wx.EXPAND)

        # Botão para verificar
        verify_button = wx.Button(panel, label='Verificar')
        verify_button.Bind(wx.EVT_BUTTON, self.on_verify)
        vbox.Add(verify_button, flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        # Área de resultado
        self.result_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE, size=(-1, 250))
        vbox.Add(self.result_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    def create_menu_bar(self):
        menu_bar = wx.MenuBar()

        # Menu Arquivo
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, "&Abrir Arquivo...\tCtrl+O")
        file_menu.Append(wx.ID_SAVEAS, "&Salvar Log Como...\tCtrl+S")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "&Sair\tCtrl+Q")
        menu_bar.Append(file_menu, "&Arquivo")

        # Menu Editar
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_COPY, "&Copiar Resultado")
        edit_menu.Append(wx.ID_CLEAR, "&Limpar Campos")
        menu_bar.Append(edit_menu, "&Editar")

        # Menu Ajuda
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_HELP, "&Como Usar...")
        help_menu.Append(wx.ID_ABOUT, "&Sobre...")
        menu_bar.Append(help_menu, "&Ajuda")

        self.SetMenuBar(menu_bar)

        # Eventos
        self.Bind(wx.EVT_MENU, self.on_select_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_save_log_as, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_copy_result, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.on_clear_fields, id=wx.ID_CLEAR)
        self.Bind(wx.EVT_MENU, self.on_how_to_use, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)

    def on_select_file(self, event):
        with wx.FileDialog(self, "Selecione o arquivo", wildcard="Todos os arquivos (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            path = file_dialog.GetPath()
            self.file_path_ctrl.SetValue(path)

    def on_save_log_as(self, event):
        with wx.FileDialog(self, "Salvar log como", wildcard="Arquivo de texto (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            path = file_dialog.GetPath()
            with open(path, 'w', encoding='utf-8') as file:
                file.write(self.result_text.GetValue())

    def on_exit(self, event):
        self.Close()

    def on_copy_result(self, event):
        if self.result_text.GetValue():
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(self.result_text.GetValue()))
                wx.TheClipboard.Close()

    def on_clear_fields(self, event):
        self.file_path_ctrl.SetValue("")
        self.expected_hash_ctrl.SetValue("")
        self.result_text.SetValue("")

    def on_how_to_use(self, event):
        wx.MessageBox(
            "1. Selecione um arquivo clicando em 'Selecionar'.\n"
            "2. Escolha o algoritmo de hash desejado.\n"
            "3. Insira o hash esperado.\n"
            "4. Pressione 'Verificar' ou aperte Enter no campo de hash.\n\n"
            "O resultado será exibido e registrado no log.",
            "Como Usar",
            wx.OK | wx.ICON_INFORMATION
        )

    def on_about(self, event):
        wx.MessageBox(
            "HashCheck\n"
            "by HermesRoot\n"
            "Licença: MIT\n\n"
            "Versão  0.1.0",
            "Sobre",
            wx.OK | wx.ICON_INFORMATION
        )

    def calculate_checksum(self, file_path, algorithm):
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def on_verify(self, event):
        file_path = self.file_path_ctrl.GetValue()
        algorithm = self.algorithm_choice.GetValue()
        expected_hash = self.expected_hash_ctrl.GetValue().strip().lower()

        if not file_path or not os.path.exists(file_path):
            wx.MessageBox("Selecione um arquivo válido.", "Erro", wx.ICON_ERROR)
            return

        if not expected_hash:
            wx.MessageBox("Preencha o hash esperado.", "Erro", wx.ICON_ERROR)
            return

        calculated_hash = self.calculate_checksum(file_path, algorithm)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if calculated_hash == expected_hash:
            result_text = "✔️ CORRETO"
            result_color = wx.Colour(0, 128, 0)
        else:
            result_text = "❌ INCORRETO"
            result_color = wx.Colour(200, 0, 0)

        log_entry = (
            "--------------------------------------------------------------------------------\n"
            f"Data/Hora: {now}\n"
            f"Arquivo: {file_path}\n"
            f"Algoritmo: {algorithm.upper()}\n"
            f"Hash Esperado: {expected_hash}\n"
            f"Hash Calculado: {calculated_hash}\n"
            f"Resultado: {result_text}\n"
            "--------------------------------------------------------------------------------\n\n"
        )

        self.result_text.SetForegroundColour(result_color)
        self.result_text.SetValue(log_entry)

        with open("checksums_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)


if __name__ == '__main__':
    app = wx.App()
    ChecksumVerifier(None, title='HashCheck')
    app.MainLoop()
