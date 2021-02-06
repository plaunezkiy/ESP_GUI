from threads import Wallhack, Bunny, Radar, RCS, Trigger, AimBot #, NoFlash
from kivymd.app import MDApp
from kivy.lang import Builder


class Kaki(MDApp):
    threads = {"wh": Wallhack,
               "bunny": Bunny,
               "radar": Radar,
               "no_recoil": RCS,
               "trigger": Trigger}
    for thread in threads.values():
        thread.daemon = True
        thread.start()
        thread.pause()

    def build(self):
        return Builder.load_file("layout.kv")

    def por_thread(self, button, process, arg=None):
        process = self.threads[process]
        if arg:
            control_box = button.parent.parent
            bone = 5  # control_box.ids.aimbone.text
            fov = control_box.ids.fov.value
            smooth = control_box.ids.smoothness.value
            process.params = (bone, fov, smooth)
        if button.text == "OFF":
            process.resume()
            button.text = "ON"
        else:
            process.pause()
            button.text = "OFF"

    def eod_aim_controls(self, button):
        controls_box = button.parent.parent.ids.aim_controls.children
        if button.text == "OFF":
            for widget in controls_box:
                widget.disabled = False
            button.text = "ON"
        else:
            for widget in controls_box:
                widget.disabled = True
            button.text = "OFF"
