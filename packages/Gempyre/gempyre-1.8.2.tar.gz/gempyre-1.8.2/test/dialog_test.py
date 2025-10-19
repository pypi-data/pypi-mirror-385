import Gempyre
import os
import sys
from pathlib import Path
from Gempyre import resource

def main():
    name = os.path.join(os.path.dirname(sys.argv[0]), "python_dialog_test.html")
    map, names = resource.from_file(name)
    ui = Gempyre.Ui(map, names[name])
    output = Gempyre.Element(ui, "output")
    open_file_button = Gempyre.Element(ui, "open_file")
    def open_file(_):
        dlg = Gempyre.Dialog()
        result = dlg.open_file_dialog("hop", str(Path.home()), [("Text", ["*.txt", "*.text"])])
        if result:
            output.set_html(result)
        
    open_file_button.subscribe("click", open_file)
    
    open_files_button = Gempyre.Element(ui, "open_files")
    def open_files(_):
        result = Gempyre.Dialog().open_files_dialog("hop", str(Path.home()))
        if result:
            output.set_html(str(result))
        
    open_files_button.subscribe("click", open_files)
    
    open_dir_button = Gempyre.Element(ui, "open_dir")
    def open_dir(_):
        dialog = Gempyre.Dialog()
        result = dialog.open_dir_dialog("hop", str(Path.home()))
        if result:
            output.set_html(result)
        
    open_dir_button.subscribe("click", open_dir)
    
    
    save_file_button = Gempyre.Element(ui, "save_file")
    def save_file(_):
        dialog = Gempyre.Dialog()
        filter = [("Foo", ["*.foo", "*.bar"])]
        result = dialog.save_file_dialog("hop", str(Path.home()), filter)
        if result:
            output.set_html(result)
        
    save_file_button.subscribe("click", save_file)
    
    ui.run()

if __name__ == "__main__":
    main()
    
