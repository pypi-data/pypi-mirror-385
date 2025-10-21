import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.style = ttk.Style()

    def InitUI(self):
        self.root.mainloop()

    def Title(self, title):
        self.root.title(title)

    def Size(self, width, height):
        self.root.geometry(f"{width}x{height}")

    def BgColor(self, color):
        self.root.configure(bg=color)

    # --- Tkinter Variables ---
    def StringVar(self, value=None):
        return tk.StringVar(self.root, value=value)
    
    def IntVar(self, value=None):
        return tk.IntVar(self.root, value=value)
    
    def DoubleVar(self, value=None):
        return tk.DoubleVar(self.root, value=value)
        
    def BooleanVar(self, value=None):
        return tk.BooleanVar(self.root, value=value)


    # --- Geometry Managers ---
    def Pack(self, widget, **options):
        """Packs a widget into the parent container."""
        widget.pack(**options)

    def Grid(self, widget, **options):
        """Grids a widget into the parent container."""
        widget.grid(**options)
        
    def Place(self, widget, **options):
        """Places a widget at a specific x,y coordinate."""
        widget.place(**options)
        
    def Grid_configure_row(self, parent, row, **options):
        """Configures row properties for the grid layout."""
        parent.grid_rowconfigure(row, **options)
        
    def Grid_configure_column(self, parent, col, **options):
        """Configures column properties for the grid layout."""
        parent.grid_columnconfigure(col, **options)

    # --- Widget Creation (Tk and Ttk) ---
    def AddLabel(self, parent, text, **options):
        """Creates and returns a Ttk Label."""
        label = ttk.Label(parent, text=text, **options)
        return label

    def AddButton(self, parent, text, command, **options):
        """Creates and returns a Ttk Button."""
        button = ttk.Button(parent, text=text, command=command, **options)
        return button

    def AddEntry(self, parent, **options):
        """Creates and returns a Ttk Entry."""
        entry = ttk.Entry(parent, **options)
        return entry

    def AddText(self, parent, **options):
        """Creates and returns a multi-line Text widget (Tk, no Ttk equivalent)."""
        text_widget = tk.Text(parent, **options)
        return text_widget

    def AddFrame(self, parent, **options):
        """Creates and returns a Ttk Frame."""
        frame = ttk.Frame(parent, **options)
        return frame

    def AddCheckbutton(self, parent, text, variable, **options):
        """Creates and returns a Ttk Checkbutton."""
        checkbutton = ttk.Checkbutton(parent, text=text, variable=variable, **options)
        return checkbutton

    def AddRadiobutton(self, parent, text, variable, value, **options):
        """Creates and returns a Ttk Radiobutton."""
        radiobutton = ttk.Radiobutton(parent, text=text, variable=variable, value=value, **options)
        return radiobutton

    def AddScale(self, parent, **options):
        """Creates and returns a Ttk Scale (slider) widget."""
        scale = ttk.Scale(parent, **options)
        return scale
        
    def AddSpinbox(self, parent, from_value=0, to_value=100, **options):
        """Creates and returns a Ttk Spinbox widget."""
        spinbox = ttk.Spinbox(parent, from_=from_value, to=to_value, **options)
        return spinbox

    def AddCombobox(self, parent, values=None, **options):
        """Creates and returns a Ttk Combobox (dropdown list)."""
        combo = ttk.Combobox(parent, values=values, **options)
        return combo
    
    def AddMenubutton(self, parent, text, **options):
        """Creates and returns a Ttk Menubutton."""
        menubutton = ttk.Menubutton(parent, text=text, **options)
        return menubutton

    def AddMenu(self, parent, **options):
        """Creates and returns a Menu widget (Tk, no Ttk equivalent)."""
        menu = tk.Menu(parent, **options)
        return menu

    def AddMenuBar(self, window):
        """Configures a menu bar for the given window."""
        menu_bar = tk.Menu(window)
        window.config(menu=menu_bar)
        return menu_bar

    def AddListbox(self, parent, **options):
        """Creates and returns a Listbox widget (Tk, no Ttk equivalent)."""
        listbox = tk.Listbox(parent, **options)
        return listbox

    def AddCanvas(self, parent, **options):
        """Creates and returns a Canvas widget (Tk, no Ttk equivalent)."""
        canvas = tk.Canvas(parent, **options)
        return canvas

    def AddLabelFrame(self, parent, text, **options):
        """Creates and returns a Ttk LabelFrame."""
        labelframe = ttk.LabelFrame(parent, text=text, **options)
        return labelframe
    
    def AddPanedWindow(self, parent, orient='horizontal', **options):
        """Creates and returns a Ttk PanedWindow."""
        panedwindow = ttk.PanedWindow(parent, orient=orient, **options)
        return panedwindow

    def AddNotebook(self, parent, **options):
        """Creates and returns a Ttk Notebook (tabbed) widget."""
        notebook = ttk.Notebook(parent, **options)
        return notebook

    def AddScrollbar(self, parent, orient='vertical', **options):
        """Creates and returns a Ttk Scrollbar widget."""
        if orient == 'vertical':
            scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, **options)
        elif orient == 'horizontal':
            scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, **options)
        else:
            raise ValueError("Invalid orientation for scrollbar. Use 'vertical' or 'horizontal'.")
        return scrollbar
    
    def AddProgressBar(self, parent, mode='indeterminate', **options):
        """Creates and returns a Ttk Progressbar widget."""
        progressbar = ttk.Progressbar(parent, mode=mode, **options)
        return progressbar
    
    def AddToplevel(self, parent, **options):
        """Creates and returns a Toplevel (sub) window."""
        toplevel = tk.Toplevel(parent, **options)
        return toplevel
    
    def AddSeparator(self, parent, orient='horizontal', **options):
        """Creates and returns a Ttk Separator widget."""
        separator = ttk.Separator(parent, orient=orient, **options)
        return separator
        
    def AddSizegrip(self, parent, **options):
        """Creates and returns a Ttk Sizegrip widget for resizing windows."""
        sizegrip = ttk.Sizegrip(parent, **options)
        return sizegrip
    
    def AddTreeview(self, parent, **options):
        """Creates and returns a Ttk Treeview widget for hierarchical data."""
        treeview = ttk.Treeview(parent, **options)
        return treeview


    # --- Ttk Style and Theme Management ---
    def SetTheme(self, theme_name):
        """Sets the ttk theme for the entire application."""
        self.style.theme_use(theme_name)
    
    def GetThemes(self):
        """Returns a list of all available ttk themes."""
        return self.style.theme_names()

    def ConfigureStyle(self, style_name, **options):
        """Configures a ttk style (e.g., 'TButton')."""
        self.style.configure(style_name, **options)

    # --- Common Dialogs ---
    def ShowMessage(self, title, message):
        """Displays a standard message box."""
        messagebox.showinfo(title, message)

    def AskQuestion(self, title, message):
        """Asks a yes/no question and returns True or False."""
        return messagebox.askyesno(title, message)
    
    def AskYesNoCancel(self, title, message):
        """Asks a yes/no/cancel question and returns True, False, or None."""
        return messagebox.askyesnocancel(title, message)
        
    def AskOpenFile(self, **options):
        """Opens a file selection dialog and returns the file path."""
        return filedialog.askopenfilename(**options)

    def AskSaveFile(self, **options):
        """Opens a save file dialog and returns the file path."""
        return filedialog.asksaveasfilename(**options)

    def AskString(self, title, prompt):
        """Asks the user for a string and returns it."""
        return simpledialog.askstring(title, prompt)