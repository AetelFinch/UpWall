import os
import ctypes
import os.path
import pathlib
import datetime
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox as mb
import wallhavenapi as wh

categories = ["general", "anime", "people"]
purity = ["sfm", "sketchy", "nsfw"]
sorting = ["date_added", "relevance", "random",
           "views", "favorites", "toplist"]
headers = ["name", "size (Kb)", "status"]


class Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Upwall")

        self.frm_params = tk.Frame(master=self)
        self.frm_params.pack(fill=tk.BOTH, expand=True)

        # comboboxes
        self.cmb_categories = self._initCombobox(0, categories, "category")
        self.cmb_purity = self._initCombobox(1, purity, "purity")
        self.cmb_sorting = self._initCombobox(2, sorting, "sorting")

        # entries
        self.ent_api_key = self._initEntry(0, "api-key")
        self.ent_atleast = self._initEntry(1, "atleast resolution")
        self.ent_resolution = self._initEntry(2, "resolution")
        self.ent_resolution.insert(0, self._screenResolution())

        # frame
        self.frm_dir_and_load = tk.Frame(master=self)
        self.frm_dir_and_load.pack(fill=tk.BOTH, expand=True)

        # change directory
        self.frm_directory = tk.Frame(master=self.frm_dir_and_load)
        self.frm_directory.pack(side=tk.LEFT)

        self.ent_directory = self._initEntryPath()

        self.btn_change_directory = tk.Button(master=self.frm_directory,
                                              text="...",
                                              command=self.chooseDirectory)
        self.btn_change_directory.pack(side=tk.LEFT)

        # loading button
        self.frm_load = tk.Frame(master=self.frm_dir_and_load)
        self.frm_load.pack(side=tk.RIGHT)

        self.btn_load_wallpaper = tk.Button(master=self.frm_load,
                                            text="load",
                                            command=self.downloadWallpaper)
        self.btn_load_wallpaper.pack(side=tk.RIGHT, padx=10, pady=10)

        # current download wallpapers
        self.frm_downloads = tk.Frame(master=self)
        self.frm_downloads.pack(padx=10, pady=10)

        self.tbl_downloadsTable = self._initDawnloadsTable()

        # commands
        self.frm_commands = tk.Frame(master=self)
        self.frm_commands.pack(fill=tk.BOTH, expand=True)

        self.btn_delete = tk.Button(master=self.frm_commands,
                                    text="delete",
                                    command=self.deleteWallpaper)
        self.btn_delete.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_set_wallpaper = tk.Button(master=self.frm_commands,
                                           text="setToWin",
                                           command=self.setToMainWindow)
        self.btn_set_wallpaper.pack(side=tk.LEFT, padx=10, pady=10)

    def _initCombobox(self, rowIdx, valueList, name):
        frame = tk.Frame(master=self.frm_params)
        frame.grid(row=rowIdx, column=0, padx=10, pady=10)

        label = tk.Label(master=frame, text=name)
        label.pack(anchor="nw")

        box = ttk.Combobox(master=frame,
                           values=valueList)
        box.current(0)
        box.pack()

        return box

    def _initEntry(self, rowIdx, name):
        frame = tk.Frame(master=self.frm_params)
        frame.grid(row=rowIdx, column=1, padx=10, pady=10)

        label = tk.Label(master=frame, text=name)
        label.pack(anchor="nw")

        entry = tk.Entry(master=frame, width=40)
        entry.pack()

        return entry

    def _initEntryPath(self):
        directory = tk.Entry(master=self.frm_directory, width=50)
        directory.pack(side=tk.LEFT, padx=10, pady=10)

        curPath = os.getcwd()
        directory.insert(0, curPath)

        return directory

    def _initDawnloadsTable(self):
        table = ttk.Treeview(master=self.frm_downloads,
                             show="headings",
                             selectmode="browse",
                             columns=headers)
        for header in headers:
            table.heading(header, text=header)
        table.bind("<Double-1>", self.openImage)

        scrollerY = ttk.Scrollbar(master=self.frm_downloads,
                                  orient=tk.VERTICAL,
                                  command=table.yview)
        table.configure(yscroll=scrollerY.set)

        table.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollerY.pack(side=tk.RIGHT, fill=tk.Y)

        return table

    def _screenResolution(self):
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        resolution = str(w) + "x" + str(h)
        return resolution

    def chooseDirectory(self):
        directory = tk.filedialog.askdirectory()
        self.ent_directory.delete(0, tk.END)
        self.ent_directory.insert(0, directory)

    def downloadWallpaper(self):
        api_key = self.fromStrToNone(self.ent_api_key.get())
        atleast = self.fromStrToNone(self.ent_atleast.get())
        resolutions = self.fromStrToNone(self.ent_resolution.get())
        category = self.fromStrToNone(self.cmb_categories.get())
        purities = self.fromStrToNone(self.cmb_purity.get())
        sorting = self.fromStrToNone(self.cmb_sorting.get())

        if api_key is None and purity == "nsfw":
            msg = "please provide your key to access the nsfw content"
            mb.showwarning("warning", msg)
            return

        file, format_file = requestAPI.getFile(api_key=api_key,
                                               categories=category,
                                               purities=purities,
                                               atleast=atleast,
                                               resolutions=resolutions,
                                               sorting=sorting)
        directory = self.ent_directory.get()
        name_file = DataManager.saveFileinDirAndGetName(file,
                                                        directory,
                                                        format_file)
        sizeKb_file = int(os.stat(name_file).st_size / 1024.0)

        self.setFileInTable(name_file, sizeKb_file, "uploaded")

    def fromStrToNone(self, string):
        if string == "":
            return None
        return string

    def setFileInTable(self, name, size, status):
        self.tbl_downloadsTable.insert('', tk.END, values=[name, size, status])

    def openImage(self, event):
        row_id = self.selectRow()
        path = self.getPathFromTable(row_id)
        DataManager.openFile(path)

    def deleteWallpaper(self):
        row_id = self.selectRow()
        if row_id is None:
            return

        path = self.getPathFromTable(row_id)

        DataManager.removeFile(path)
        self.tbl_downloadsTable.delete(row_id)

    def setToMainWindow(self):
        row_id = self.selectRow()
        if row_id is None:
            return

        path = self.getPathFromTable(row_id)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

    def selectRow(self):
        row_id = self.tbl_downloadsTable.focus()
        if row_id == "":
            msg = "Please, select image"
            mb.showwarning("Warning", msg)
            return None

        return row_id

    def getPathFromTable(self, row_id):
        titlesInContact = self.tbl_downloadsTable.item(row_id)['values']
        path = titlesInContact[0]

        return path


class requestAPI:
    def getFile(api_key, categories, purities, atleast, resolutions, sorting):
        wallpaper = wh.WallhavenApiV1(api_key=api_key)

        wallpapers = wallpaper.search(categories=categories,
                                      sorting=sorting,
                                      purities=purities,
                                      atleast=atleast,
                                      resolutions=resolutions)

        wallpaper_id = wallpapers['data'][0]['id']
        wallpaper_url = wallpapers['data'][0]['path']

        formatFile = requestAPI.getFormatFile(wallpaper_url)
        file = wallpaper.download_wallpaper(wallpaper_id)

        return file, formatFile

    def getFormatFile(file):
        return pathlib.Path(file).suffix


class DataManager:
    def saveFileinDirAndGetName(file, directory, formatFile):
        name_file = DataManager.getNameFile(directory, formatFile)

        with open(name_file, 'wb') as img_file:
            img_file.write(file)

        return name_file

    def getNameFile(directory, formatFile):
        name_file = datetime.datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
        name_file += formatFile
        return os.path.join(directory, name_file)

    def removeFile(path):
        if os.path.exists(path):
            os.remove(path)
        else:
            msg = "this image no longer exists"
            mb.showwarning("Warning", msg)

    def openFile(path):
        if os.path.exists(path):
            os.system("\"" + path + "\"")
        else:
            msg = "this image no longer exists"
            mb.showwarning("Warning", msg)


if __name__ == "__main__":
    app = Interface()
    app.mainloop()
