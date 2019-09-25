import logging
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font as tkfont
import Pmw


#GLOBALS!
g_name = "MiniText"
g_version_num = "1.0"
g_version_name = "ToddlersFirst"
g_default_font_family = 'Arial'
g_default_font_size = 12

#OPTIONS
g_toolbar_buttons_size = 19
g_toolbar_padx = 3
g_icon_path = str(Path().absolute()) + "/Icons/"

g_toolframe_color = 'lightgrey'
g_search_highlight_color = 'lightgreen'
g_text_color = 'black'
g_status_text_color = 'black'

g_menu_font = {'family': 'Ubuntu', 'size': 14}
g_status_bar_font = {'family': 'Ubuntu', 'size': 14}

g_font_frame_family_menu_width = 15

g_toolframe_colored_widgets = []

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#region Menus

class SearchWindow(tk.Toplevel):

    def __init__(self, editor, master):
        tk.Toplevel.__init__(self, master)
        self.text_area = editor.text_area

        #Options
        self.highlight_color = g_search_highlight_color

        #Init and pack widgets
        self.title("Search")
        self.resizable(0, 0)
        self.attributes("-toplevel", True)
        self.wm_protocol("WM_DELETE_WINDOW", lambda: self.SearchWindowClose())

        self.search_variable = tk.StringVar()
        self.search_entry = tk.Entry(self, textvariable=self.search_variable)
        self.search_entry.pack(side=tk.TOP)
        self.search_entry.focus_set()

        self.search_frame = tk.Frame(self)
        self.search_button = tk.Button(self.search_frame, text="SEARCH!", command= lambda: self.Search())
        self.search_button.pack(side=tk.BOTTOM)
        self.search_frame.pack(side=tk.BOTTOM)

    def SearchWindowClose(self):
        self.text_area.tag_remove("search", "1.0", tk.END)
        self.destroy()
    
    def Search(self, *args):
        search_string = self.search_variable.get()
        if not search_string:
            return
        count_var = tk.StringVar()
        self.text_area.tag_configure("search", background=self.highlight_color)
    
        start_index = "1.0"
        pos = self.text_area.search(search_string, start_index, stopindex=tk.END, count=count_var)
        while pos:
            self.text_area.tag_add("search", pos, "%s + %sc" % (pos, count_var.get()))
            start_index =  "%s +  %sc + 1c" % (pos, count_var.get())
            pos = self.text_area.search(search_string, start_index, stopindex=tk.END, count=count_var)

class RightClickMenu(tk.Menu):

    def __init__(self, master):
        tk.Menu.__init__(self, master)
        self.add_command(label="Cut                        ")
        self.add_command(label="Copy                        ")
        self.add_command(label="Paste                        ")
        self.entryconfigure("Cut                        ", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Command+X")
        self.entryconfigure("Copy                        ", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Command+C")
        self.entryconfigure("Paste                        ", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Command+V")

class ThemeMenu(tk.Toplevel):

    def __init__(self, editor, master):
        tk.Toplevel.__init__(self, master)
        self.grab_set()
        self.resizable(0,0)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.attributes('-topmost', True)

        self.editor = editor
        self.title("Themes")

        #Format is: BG, FG, Toolbar color, highlight, status bar text
        themes = {  
                    "Default": ['white', 'black', 'lightgrey', 'green', 'black'],
                    "Star Platinum": ['purple', 'white', 'black', 'gold', 'gold'],
                    "Crazy Diamond": ['light coral', 'black', 'light cyan', 'white', 'black'],
                    "Gold Experience": ['goldenrod1', 'black', 'DarkOrange1', 'yellow green', 'yellow green'],
                    "Stone Free": ['deep sky blue', 'black', 'seashell4', 'lime green', 'lime green'],
                    "Tusk": ['hot pink', 'black', 'gold', 'black', 'black'],
                    "Soft & Wet": ['white', 'black', 'MediumPurple3', 'black', 'black']
                 }

        label_width = 30
        number_of_themes = 7
        theme_frames = []
        theme_buttons = []
        theme_labels = []
        theme_other_labels = []
        for i in range(number_of_themes):
            theme_frames.append(tk.Frame(self))
            theme_labels.append(tk.Label(theme_frames[i], text=list(themes.keys())[i].upper(), bg=list(themes.values())[i][0], fg=list(themes.values())[i][1], width=label_width))

        theme_buttons = [
                            tk.Button(theme_frames[0], text="1", command= lambda: editor.SetTheme(themes['Default'], 'Default')),
                            tk.Button(theme_frames[1], text="2", command=lambda: editor.SetTheme(themes['Star Platinum'], 'Star Platinum')),
                            tk.Button(theme_frames[2], text="3", command=lambda: editor.SetTheme(themes['Crazy Diamond'], 'Crazy Diamond')),
                            tk.Button(theme_frames[3], text="4", command=lambda: editor.SetTheme(themes['Gold Experience'], 'Gold Experience')),
                            tk.Button(theme_frames[4], text="5", command=lambda: editor.SetTheme(themes['Stone Free'], 'Stone Free')),
                            tk.Button(theme_frames[5], text="6", command=lambda: editor.SetTheme(themes['Tusk'], 'Tusk')),
                            tk.Button(theme_frames[6], text="7", command=lambda: editor.SetTheme(themes['Soft & Wet'], 'Soft & Wet'))
                        ]

        for i in range(number_of_themes):
            theme_labels[i].pack(side=tk.LEFT)
            theme_buttons[i].pack(side=tk.LEFT)
            theme_frames[i].pack(side=tk.TOP, pady=1)
    
    def exit(self):
        self.editor.text_area.focus_set()
        self.destroy()

class MenuBar:

    def __init__(self, editor):
        self.menu_font = tkfont.Font(family=g_menu_font['family'], size=g_menu_font['size'])

        menu_bar = tk.Menu(editor.master, font=self.menu_font)
        editor.master.configure(menu=menu_bar)

        #File dropdown
        file_dropdown = tk.Menu(menu_bar, font=self.menu_font, tearoff=0)
        file_dropdown.add_command(label="New File", command=editor.NewFile, accelerator="Command+N")
        file_dropdown.add_command(label="Open File", command=editor.OpenFile, accelerator="Command+O")
        file_dropdown.add_command(label="Save", command=editor.Save, accelerator="Command+S")
        file_dropdown.add_command(label="Save As...", command=editor.SaveAs, accelerator="Option+Command+S")
        file_dropdown.add_separator()
        file_dropdown.add_command(label="Exit", command=editor.master.destroy, accelerator="Option+Command+Q")

        menu_bar.add_cascade(label="File", menu=file_dropdown)

        #Edit dropdown
        edit_dropdown = tk.Menu(menu_bar, font=self.menu_font, tearoff=0)
        edit_dropdown.add_command(label="Undo", command=editor.text_area.edit_undo, accelerator="Command+Z")
        edit_dropdown.add_command(label="Redo", command=editor.text_area.edit_redo, accelerator="Command+Shift+Z")
        edit_dropdown.add_separator()
        edit_dropdown.add_command(label="Cut", accelerator="Command+X")
        edit_dropdown.add_command(label="Copy", accelerator="Command+C")
        edit_dropdown.add_separator()
        edit_dropdown.add_command(label="Paste", accelerator="Command+V")
        edit_dropdown.add_separator()
        edit_dropdown.add_command(label="Find", command=editor.OpenSearchWindow, accelerator="Command+F")

        edit_dropdown.entryconfigure("Cut", command=lambda: editor.text_area.event_generate("<<Cut>>"))
        edit_dropdown.entryconfigure("Copy", command=lambda: editor.text_area.event_generate("<<Copy>>"))
        edit_dropdown.entryconfigure("Paste", command=lambda: editor.text_area.event_generate("<<Paste>>"))

        menu_bar.add_cascade(label="Edit", menu=edit_dropdown)
        

        #About dropdown
        about_dropdown = tk.Menu(menu_bar, font=self.menu_font, tearoff=0)
        about_dropdown.add_command(label="Release Notes", command=self.ShowReleaseNotesMessage)
        about_dropdown.add_separator()
        about_dropdown.add_command(label="About", command=self.ShowAboutMessage)
        
        menu_bar.add_cascade(label="About", menu=about_dropdown)

        #Preferences dropdown
        preferences_dropdown = tk.Menu(menu_bar, font=self.menu_font, tearoff=0)
        preferences_dropdown.add_command(label="Themes", command= lambda: self.ShowThemesMenu(editor))

        menu_bar.add_cascade(label="Preferences", menu=preferences_dropdown)

    def ShowAboutMessage(self):
        box_title = "About " + g_name
        box_message = "A simple Python text editor"
        messagebox.showinfo(box_title, box_message)
    
    def ShowReleaseNotesMessage(self):
        box_title = "Release Notes"
        box_message = "Version " + g_version_num + " - " + g_version_name
        messagebox.showinfo(box_title, box_message)

    def ShowThemesMenu(self, editor):
        theme_menu = ThemeMenu(editor, editor.master)
        master.wait_window(theme_menu)

#endregion

#Text bar at bottom of editor that reacts to actions like saving.
class StatusBar:

    def __init__(self, editor):
        self.status_font = tkfont.Font(family=g_status_bar_font['family'], size=g_status_bar_font['size'])
        self.editor = editor
        
        self.status = tk.StringVar()
        self.status.set(g_name + " Version " + g_version_num + " - " + g_version_name)
        
        self.label = tk.Label(editor.text_area, textvariable=self.status, fg=g_status_text_color, bg=g_toolframe_color, anchor="sw", font=self.status_font)
        self.label.pack(side=tk.BOTTOM, fill=tk.BOTH)
        
        global g_toolframe_colored_widgets
        g_toolframe_colored_widgets.append(self.label)
    
    def UpdateStatus(self, *args):
        if (isinstance(args[0], str) and args[0]=="Save"):
            self.status.set("Your file has been saved!")
            self.editor.is_file_saved = True
        elif (isinstance(args[0], str) and args[0] != "Save"):
            if args[0]!="Default":
                self.status.set("Theme changed to " + "『" + args[0] + "』.")
            else:
                self.status.set("Theme changed to " + args[0] + ".")
        else:
            self.status.set(g_name + " Version " + g_version_num + " - " + g_version_name)
            self.editor.is_file_saved = False

#A full set of the same font, containing all variations ("flavors") of bold, italic, and underline.
class FontSet:

    def __init__(self, family, size):
        self.family = family
        self.size = size

        self.flavors = { "vanilla": tkfont.Font(family=self.family, size=self.size),
                         "bold": tkfont.Font(family=self.family, size=self.size, weight='bold'),
                         "italic": tkfont.Font(family=self.family, size=self.size, slant='italic'),
                         "underline": tkfont.Font(family=self.family, size=self.size, underline=1),
                         "bold-italic": tkfont.Font(family=self.family, size=self.size, weight='bold', slant='italic'),
                         "bold-underline": tkfont.Font(family=self.family, size=self.size, weight='bold', underline=1),
                         "italic-underline": tkfont.Font(family=self.family, size=self.size, slant='italic', underline=1),
                         "bold-italic-underline": tkfont.Font(family=self.family, size=self.size, weight='bold', slant='italic', underline=1)
                        }

    def GetFamily(self):
        return self.family

    def GetSize(self):
        return self.size

    def GetFlavor(self, flavor):
        return self.flavors[flavor]
    
    def Configure(self, **kwargs):
        if 'size' in kwargs:
            self.size = kwargs['size']
            for f in self.flavors:
                self.flavors[f].configure(size=self.size)

        if 'family' in kwargs:
            self.family = kwargs['family']
            for f in self.flavors:
                self.flavors[f].configure(family=self.family)

#Frame for font picking, contains two option menus for picking family and size
class FontFrame(tk.Frame):
    #Note that master refers to the master of the frame, not the option menus
    def __init__(self, master, frame_font_set): 
        super().__init__(master, bg=g_toolframe_color)

        self.frame_font_set = frame_font_set

        #Options
        self.family_menu_width = g_font_frame_family_menu_width
        self.bg = g_toolframe_color
        self.icon_path = g_icon_path
        self.button_size = g_toolbar_buttons_size

        #Set up menus
        font_families = tkfont.families()
        font_sizes = [1, 5, 5.5, 6.5, 7.5, 8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
              
        self.blank_display = tk.StringVar(self)
        self.blank_display.set(" ")
        self.family_display = tk.StringVar(self)
        self.family_display.set("  " + g_default_font_family)

        self.family_menu = tk.OptionMenu(self, self.family_display, *font_families, command=self.SwitchFamilyOption)
        self.family_menu.configure(highlightthickness=0, bd=0, bg=self.bg, width=self.family_menu_width, anchor=tk.W)
        self.family_menu.pack(side=tk.LEFT)

        vcmd = (self.register(self.ValidateAndChangeTextSizeEntry), '%P', '%S')
        self.size_frame = tk.Frame(self, bg=self.bg)
        self.size_variable = tk.StringVar(self.size_frame)
        self.size_variable.set(str(g_default_font_size))
        self.size_entry = tk.Entry(self.size_frame, validate="key", validatecommand=vcmd, width=6, bd=0, highlightthickness=0, relief=tk.FLAT, textvariable=self.size_variable)
        self.size_entry.pack(side=tk.LEFT)
        self.size_menu = tk.OptionMenu(self.size_frame, self.blank_display, *font_sizes, command=self.SwitchSizeOption)
        self.size_menu.configure(highlightthickness=0, bd=0, bg=self.bg, width=0)
        self.size_menu.pack(side=tk.LEFT)
        self.size_frame.pack(side=tk.LEFT)

        global g_toolframe_colored_widgets
        g_toolframe_colored_widgets.extend([self.family_menu, self.size_frame, self.size_menu])

        #Events
        self.size_entry.bind("<FocusIn>", self.SizeEntryFocusIn)
        self.size_entry.bind("<FocusOut>", self.SizeEntryFocusOut)

    #Select all text in the entry field 
    def SizeEntryFocusIn(self, *args):
        self.size_entry.selection_range(0, tk.END)
        self.size_entry.icursor(0)

    #If the entry string is empty when it loses focus, set it back to the current size. 
    def SizeEntryFocusOut(self, *args):
        if not self.size_variable.get():
            self.size_variable.set(self.frame_font_set.GetSize())

    def SwitchFamilyOption(self, *args):
        #Actual family setting
        self.frame_font_set.Configure(family=self.family_display.get())

        #Include "..." on the display string if it goes out of the menu width
        if ((len(self.family_display.get()) - self.family_menu_width) >= 6):
            cut_variable = str(self.family_display.get()[0:(self.family_menu_width + 3)]) + "..."
            self.family_display.set(cut_variable)
        self.family_display.set("  " + self.family_display.get())

    def SwitchSizeOption(self, *args):
        self.frame_font_set.Configure(size=self.blank_display.get())
        self.size_variable.set(str(self.frame_font_set.GetSize()))
        self.blank_display.set(" ")

    def ValidateAndChangeTextSizeEntry(self, P, S):
        #Allow text size to stay the same if field is empty
        if not P:
            return True

        elif P.isdigit() and (int(P) <= 1638) and (int(P) > 0):
            new_size = int(P)
            self.frame_font_set.Configure(size=new_size)
            return True
        else:
            return False

#Where the text is typed. Menu bar and status bar are both instantiated here.
class Editor:

    def __init__(self, master):
        master.title("Untitled - " + g_name)
        master.geometry("1200x700")

        self.master = master
        self.is_file_saved = True
        self.filename = None

        #Options
        self.tool_frame_color = g_toolframe_color
        self.button_size = g_toolbar_buttons_size
        self.tool_padx = g_toolbar_padx
        self.icon_path = g_icon_path

        #Initialize and pack widgets
        self.balloon = Pmw.Balloon(self.master)
        self.font_set = FontSet(g_default_font_family, g_default_font_size)

        self.tool_frame = tk.Frame(self.master, bd=5, bg=self.tool_frame_color)
        self.tool_frame.pack(side=tk.TOP, fill=tk.X)

        self.text_area = tk.Text(self.master, fg=g_text_color, insertbackground=g_text_color, font=self.font_set.GetFlavor("vanilla"), highlightthickness=0, undo=True)
        self.scroll_bar = tk.Scrollbar(self.master, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scroll_bar.set)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.InitializeButtons()

        self.ReconfigureTags()

        self.font_frame = FontFrame(self.tool_frame, self.font_set)
        self.font_frame.pack(side=tk.LEFT, padx=self.tool_padx)
        self.balloon.bind(self.font_frame.family_menu, "Font")
        self.balloon.bind(self.font_frame.size_frame, "Font Size")

        self.status_bar = StatusBar(self)
        self.menu_bar = MenuBar(self)
        self.right_click_menu = RightClickMenu(self.master)

        self.BindKeyShortcuts()

        global g_toolframe_colored_widgets
        g_toolframe_colored_widgets.append(self.tool_frame)

    def SetWindowTitle(self, name=None):
        if name:
            self.master.title(name + " - " + g_name)
        else:
            self.master.title("Untitled - " + g_name)

    def OnClose(self):
        if self.is_file_saved:
            self.master.destroy()
            return
        
        result = messagebox.askyesnocancel("Warning!", "You're about to exit without saving! Want to save?", icon="warning")

        if result == True:
            if self.Save():
                self.master.destroy()
        elif result == False:
            self.master.destroy()

        return

    def NewFile(self, *args):
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.SetWindowTitle()

    def OpenFile(self, *args):
        self.filename = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"),
                       ("Text Files", "*.txt"),
                       ("Python Scripts", "*.py"),
                       ("Rich Text Files", "*.rtf")
                       ])

        if self.filename:
            self.text_area.delete(1.0, tk.END)
            with open(self.filename, "r") as f:
                self.text_area.insert(1.0, f.read())
            self.SetWindowTitle(self.filename)
    
    def Save(self, *args):
        if self.filename:
            try:
                text_area_content = self.text_area.get(1.0, tk.END)
                with open(self.filename, "w") as f:
                    f.write(text_area_content)
                self.status_bar.UpdateStatus("Save")
            except Exception as e:
                print(e)
        else:
            return self.SaveAs()
    
    def SaveAs(self, *args):
        try:
            new_file = filedialog.asksaveasfilename(
                initialfile="Untitled.txt",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"),
                           ("Python Scripts", "*.py"),
                           ("Rich Text Files", "*.rtf"),
                           ("All Files", "*.*")      
                          ])
            if not new_file:
                return False

            text_area_content = self.text_area.get(1.0, tk.END)
            with open(new_file, "w") as f:
                f.write(text_area_content)
            self.filename = new_file
            self.SetWindowTitle(self.filename)
            self.status_bar.UpdateStatus("Save")
            return True
        except Exception as e:
            print(e)
            return False

    #Create and pack bold, italic, underline, redo, and undo buttons
    def InitializeButtons(self):
        undo_photo = tk.PhotoImage(file=self.icon_path + "undo_icon.png")
        redo_photo = tk.PhotoImage(file=self.icon_path + "redo_icon.png")
        self.ur_button_frame = tk.Frame(self.tool_frame, bg=self.tool_frame_color)
        self.undo_button = tk.Button(self.ur_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size ,image=undo_photo, fg="black", command=self.text_area.edit_undo)
        self.undo_button.image = undo_photo
        self.redo_button = tk.Button(self.ur_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size ,image=redo_photo, fg="black", command=self.text_area.edit_redo)
        self.redo_button.image = redo_photo
        self.undo_button.pack(side=tk.LEFT)
        self.redo_button.pack(side=tk.LEFT)
        self.ur_button_frame.pack(side=tk.LEFT, padx=self.tool_padx)

        bold_photo = tk.PhotoImage(file=self.icon_path + "bold_icon.png")
        italic_photo = tk.PhotoImage(file=self.icon_path + "italic_icon.png")
        underline_photo = tk.PhotoImage(file=self.icon_path + "underline_icon.png")
        self.biu_button_frame = tk.Frame(self.tool_frame, bg=self.tool_frame_color)
        self.bold_button = tk.Button(self.biu_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size ,image=bold_photo, fg="black", command= lambda: self.FormatText("bold"))
        self.italic_button = tk.Button(self.biu_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size, image=italic_photo, fg="black", command= lambda: self.FormatText("italic"))
        self.underline_button = tk.Button(self.biu_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size, image=underline_photo, fg="black", command= lambda: self.FormatText("underline"))
        self.bold_button.image = bold_photo
        self.italic_button.image = italic_photo
        self.underline_button.image = underline_photo
        self.bold_button.pack(side=tk.LEFT)
        self.italic_button.pack(side=tk.LEFT)
        self.underline_button.pack(side=tk.LEFT)
        self.biu_button_frame.pack(side=tk.LEFT, padx=self.tool_padx)

        left_photo = tk.PhotoImage(file=self.icon_path + "left_icon.png")
        center_photo = tk.PhotoImage(file=self.icon_path + "center_icon.png")
        right_photo = tk.PhotoImage(file=self.icon_path + "right_icon.png")
        self.lcr_button_frame = tk.Frame(self.tool_frame, bg=self.tool_frame_color)
        self.left_button = tk.Button(self.lcr_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size, image=left_photo, fg="black", command= lambda: self.AlignText("left"))
        self.center_button = tk.Button(self.lcr_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size, image=center_photo, fg="black", command= lambda: self.AlignText("center"))
        self.right_button = tk.Button(self.lcr_button_frame, highlightthickness=0, height=self.button_size, width=self.button_size, image=right_photo, fg="black", command= lambda: self.AlignText("right"))
        self.left_button.image = left_photo
        self.center_button.image = center_photo
        self.right_button.image = right_photo
        self.left_button.pack(side=tk.LEFT)
        self.center_button.pack(side=tk.LEFT)
        self.right_button.pack(side=tk.LEFT)
        self.lcr_button_frame.pack(side=tk.LEFT, padx=self.tool_padx)

        self.owo_button_frame = tk.Frame(self.tool_frame, bg=self.tool_frame_color)
        self.owo_button = tk.Button(self.owo_button_frame, highlightbackground=self.tool_frame_color, highlightthickness=0, text="owo", fg="black", command= self.Owoify)
        self.owo_button.pack(side=tk.LEFT)
        self.owo_button_frame.pack(side=tk.LEFT, padx=self.tool_padx)

        self.balloon = Pmw.Balloon(self.master)
        self.balloon.bind(self.bold_button, "Bold")
        self.balloon.bind(self.italic_button, "Italic")
        self.balloon.bind(self.underline_button, "Underline")
        self.balloon.bind(self.left_button, "Align Left")
        self.balloon.bind(self.center_button, "Center Text")
        self.balloon.bind(self.right_button, "Align Right")
        self.balloon.bind(self.undo_button, "Undo")
        self.balloon.bind(self.redo_button, "Redo")
        self.balloon.bind(self.owo_button, "owo-ify")

        global g_toolframe_colored_widgets
        g_toolframe_colored_widgets.extend([self.ur_button_frame, self.biu_button_frame])

    #Mapped to Command-t. For prototyping new functionality.    
    def TestFunction(self, *args):
        pass
    
    #Weplaces aww instances of "r" and "l" with "w" wike so.
    def Owoify(self, *args):
        ranges = self.text_area.tag_ranges(tk.SEL)
        if not ranges:
            logging.debug("Error with Owoify()! Nothing selected.")
            return
        selected_text_list = list(self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST))
        for i in range(len(selected_text_list)):
            if selected_text_list[i] == "r" or selected_text_list[i] == "l":
                selected_text_list[i] = "w"
            if selected_text_list[i] == "R" or selected_text_list[i] == "L":
                selected_text_list[i] = "W"

        new_text = ''.join(selected_text_list)

        self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        self.text_area.insert(tk.INSERT, new_text)
        

    def SetTheme(self, theme, theme_name):
        self.text_area.configure(bg=theme[0], fg=theme[1], insertbackground=theme[1])
        g_text_color = theme[1]
        global g_toolframe_color, g_toolframe_colored_widgets, g_search_highlight_color, g_status_text_color
        g_toolframe_color = theme[2]
        for w in g_toolframe_colored_widgets:
            w.configure(bg=theme[2])
        g_search_highlight_color = theme[3]
        g_status_text_color = theme[4]
        self.status_bar.label.configure(fg=theme[4])
        self.status_bar.UpdateStatus(theme_name)

    #Option-Command-s is bound to this to prevent a weird-ass bug from happening. 
    def DoNothing(self, *args):
        pass

    #Helper function that refreshes the tags with fonts for use after they have been changed.
    def ReconfigureTags(self):
        self.text_area.tag_configure("bold", font=self.font_set.GetFlavor("bold"))
        self.text_area.tag_configure("italic", font=self.font_set.GetFlavor("italic"))
        self.text_area.tag_configure("underline", font=self.font_set.GetFlavor("underline"))
        self.text_area.tag_configure("bold-italic", font=self.font_set.GetFlavor("bold-italic"))
        self.text_area.tag_configure("bold-underline", font=self.font_set.GetFlavor("bold-underline"))
        self.text_area.tag_configure("italic-underline", font=self.font_set.GetFlavor("italic-underline"))
        self.text_area.tag_configure("bold-italic-underline", font=self.font_set.GetFlavor("bold-italic-underline"))
        self.text_area.tag_configure("left", justify='left')
        self.text_area.tag_configure("center", justify='center')
        self.text_area.tag_configure("right", justify='right')
    
    #Aligns highlighted text depending on the argument. If no text is highlighted, the current line is aligned.
    #Arguments: "left", "center", "right"
    def AlignText(self, *args):
        if not args[0]:
            logging.debug("Error with calling AlignText()! Must have argument \"left\", \"center\", or \"right\".")
            return

        ranges = self.text_area.tag_ranges(tk.SEL)
        start = ""
        end = ""
        
        #Align just the current line if there is no selection
        if not ranges:
            start = str(self.text_area.index(tk.INSERT)) + "linestart"
            end = str(self.text_area.index(tk.INSERT)) + "lineend"     
        else:
            start = str(ranges[0]) + " linestart"
            end = str(ranges[1]) + " lineend"

        self.text_area.tag_remove("left", start, end)
        self.text_area.tag_remove("center", start, end)
        self.text_area.tag_remove("right", start, end)

        if args[0] == "left":
            self.text_area.tag_add("left", start, end)
        elif args[0] == "center":
            self.text_area.tag_add("center", start, end)
        elif args[0] == "right":
            self.text_area.tag_add("right", start, end)
   
    #Adds or removes the bold, italic, or underline effect to selected text depending on the argument.
    #Args: "bold", "italic", "underline"
    def FormatText(self, *args):
        ranges = self.text_area.tag_ranges(tk.SEL)
        if not ranges:
            return

        current_tags = self.text_area.tag_names(ranges[0])

        #Is underline, is italic, is bold
        biu_bitmap = 0
        biu_bitmap = biu_bitmap | (1 & int("bold" in current_tags or "bold-italic" in current_tags or "bold-underline" in current_tags or "bold-italic-underline" in current_tags))
        biu_bitmap = biu_bitmap | (2 & (int("italic" in current_tags or "bold-italic" in current_tags or "italic-underline" in current_tags or "bold-italic-underline" in current_tags) << 1))
        biu_bitmap = biu_bitmap | (4 & (int("underline" in current_tags or "bold-underline" in current_tags or "italic-underline" in current_tags or "bold-italic-underline" in current_tags) <<2))

        #Remove appropriate tag
        removed_tag = "none"
        if (biu_bitmap == 1):
            removed_tag = "bold"
        elif (biu_bitmap == 2):
            removed_tag = "italic"
        elif (biu_bitmap == 3):
            removed_tag = "bold-italic"
        elif (biu_bitmap == 4):
            removed_tag = "underline"
        elif (biu_bitmap == 5):
            removed_tag = "bold-underline"
        elif (biu_bitmap == 6):
            removed_tag = "italic-underline"
        elif (biu_bitmap == 7):
            removed_tag = "bold-italic-underline"
        
        if removed_tag != "none":
            self.text_area.tag_remove(removed_tag, ranges[0], ranges[1])

        request = args[0]
        if not isinstance(request, str):
            logging.debug("Error! No argument supplied for FormatText.")
            return

        if request == "bold":
            biu_bitmap = biu_bitmap ^ 1
        elif request == "italic":
            biu_bitmap = biu_bitmap ^ 2
        elif request == "underline":
            biu_bitmap = biu_bitmap ^ 4
        else:
            logging.debug("Error! FormatText must be called with argument \"bold\", \"italic\", or \"underline\".")
            return
        
        #Replace tag with appropriate one
        replacement_tag = "none"
        if (biu_bitmap == 1):
            replacement_tag = "bold"
        elif (biu_bitmap == 2):
            replacement_tag = "italic"
        elif (biu_bitmap == 3):
            replacement_tag = "bold-italic"
        elif (biu_bitmap == 4):
            replacement_tag = "underline"
        elif (biu_bitmap == 5):
            replacement_tag = "bold-underline"
        elif (biu_bitmap == 6):
            replacement_tag = "italic-underline"
        elif (biu_bitmap == 7):
            replacement_tag = "bold-italic-underline"
        
        if replacement_tag != "none":
            self.text_area.tag_add(replacement_tag, ranges[0], ranges[1])

        return

    def OpenSearchWindow(self, *args):
        search_window = SearchWindow(self, self.master)   

    def ShowRightClickMenu(self, event):
        self.right_click_menu.tk_popup(event.x + 10, event.y + 90)
    
    def BindKeyShortcuts(self):
        self.text_area.bind('<Left>', self.DoNothing)
        self.text_area.bind('<Right>', self.DoNothing)
        self.text_area.bind('<Up>', self.DoNothing)
        self.text_area.bind('<Down>', self.DoNothing)
        self.text_area.bind('<Option-Command-s>', self.DoNothing)
        self.text_area.bind('<Command-n>', self.NewFile)
        self.text_area.bind('<Command-o>', self.OpenFile)
        self.text_area.bind('<Command-s>', self.Save)
        self.text_area.bind('<Option-Command-q>', self.master.destroy)
        self.text_area.bind('<Command-b>', lambda event, b="bold": self.FormatText(b))
        self.text_area.bind('<Command-i>', lambda event, i="italic": self.FormatText(i))
        self.text_area.bind('<Command-u>', lambda event, u="underline": self.FormatText(u))
        self.text_area.bind('<Command-t>', self.TestFunction)
        self.text_area.bind('<Control-Button-1>', self.ShowRightClickMenu)
        self.text_area.bind('<Command-f>', self.OpenSearchWindow)
        self.text_area.bind('<Key>', self.status_bar.UpdateStatus)  

if __name__ == "__main__":
    master = tk.Tk()
    Pmw.initialise(master)
    editor = Editor(master)
    master.wm_protocol("WM_DELETE_WINDOW", editor.OnClose)
    master.mainloop()
    
