class CTViewer:
    # Main window chosen in ct_viewer.py, which contains the main() class. 
    def __init__(self, main_window):

        if G.GPU_MODE:
            cp.cuda.Device(G.DEVICE).use()

        from . import MenuBar
        from . import CTVolume
        from . import OptionsPanel
        from . import NodeEditor
        from . import NewMainView
        from . import AnalysisView
        from . import FileDialog
        from . import InformationBox
        from . import VolumeLayer
        from . import ImageTools
        from . import Themes

        # Set this instance as the ct_viewer. 
        print('Initialized')
        G.APP = self

        self.texture_registry = dpg.add_texture_registry(tag = G.TEX_REG_TAG) # 'main_texture_registry'
        self.colormap_registry = dpg.add_colormap_registry(tag = G.COLORMAP_TAG)
        self.value_registry = dpg.add_value_registry(tag = G.VALUE_REG_TAG)
        self.handler_registry = dpg.add_handler_registry(tag = G.HANDLER_REG_TAG)
        self.item_handler_registry = dpg.add_item_handler_registry(tag = G.ITEM_HANDLER_REG_TAG)
        self.item_hovered_registry = dpg.add_item_handler_registry(tag = 'item_hovered_registry')

        self.DrawWindow:NewMainView.MainView = NewMainView.MainView(self.value_registry)
        self.VolumeLayerGroups:VolumeLayer.VolumeLayerGroups = VolumeLayer.VolumeLayerGroups()
        self.VolumeLayerGroups.add_group(group_name = 'AllVolumes')
        window_types = ['view_plane', 'view_plane_ortho']

        self.Themes = Themes.Themes()
        self.Themes.register_colormaps(G.COLORMAP_DICT,
                                       self.colormap_registry)
        detect_drives = False
        if f'{sys.platform}' == 'win32':
            detect_drives = True

        self.FileDialog = FileDialog.FileDialog(G.CONFIG_DICT['directories']['image_dir'], 
                                                has_parent = True,
                                                debug = True, 
                                                show = False,
                                                detect_drives = detect_drives)
        
        self.NodeEditor = NodeEditor.NodeEditor()

        G.add_input_options_to_value_registry(self.value_registry)
        G.add_configuration_to_value_registry(self.value_registry)
        G.add_texture_center_to_value_registry(self.value_registry)
        G.add_colormap_combo_to_value_registry(self.value_registry)
        
        # Load up interpolators.
        CTVolume._initialize_interps()
        
        with main_window:
            self.MenuBar = MenuBar.MenuBar(value_registry = self.value_registry)
            with dpg.group(tag = 'RootWindowGroup',
                           horizontal = True):
                
                with dpg.child_window(tag = 'Navigation_Window',
                                      width = G.CONFIG_DICT['app_settings']['navigation_window_width'], 
                                      height = G.CONFIG_DICT['app_settings']['navigation_window_height'],
                                      border = True, 
                                      no_scrollbar = True):
                    with dpg.tab_bar(tag = G.LEFT_TAB_BAR, 
                                     callback = self.print_current_tab):
                        with dpg.tab(label = 'Navigation', 
                                     tag = G.NAVIGATION_TAB_TAG):
                            with dpg.group(tag = 'OptionsPanel_ImageTools_Group'):
                                self.OptionsPanel = OptionsPanel.OptionsPanel(debug = False)
                                self.OptionsPanel.create_options_panel()
                                self.ImageTools = ImageTools.ImageTools(self.VolumeLayerGroups, self.value_registry)

                with dpg.child_window(tag = 'MainViewTexture_Window',
                                      width = G.CONFIG_DICT['app_settings']['tab_pane_width'], #G.MAIN_TAB_VIEW_WINDOW_DEFAULTS['WINDOW_WIDTH'],
                                      height = G.CONFIG_DICT['app_settings']['tab_pane_height'], #G.MAIN_TAB_VIEW_WINDOW_DEFAULTS['WINDOW_HEIGHT'],
                                      border = True):
                    with dpg.tab_bar(tag = G.TAB_BAR_TAG, 
                                     callback = self.print_current_tab):
                        with dpg.tab(label = 'Volume Tab', 
                                     tag = G.VOLUME_TAB_TAG):
                            self.DrawWindow.create_draw_window('MainTexture', 
                                                               G.VOLUME_TAB_TAG, 
                                                               item_handler_reg_tag = self.item_hovered_registry)
                            self.DrawWindow.create_inset_window('InsetWindow', 
                                                                self.DrawWindow.get_window_tags()[0],
                                                                start = [round((2/3) * G.TEXTURE_DIM), 
                                                                         round((2/3) * G.TEXTURE_DIM)],
                                                                stop = [G.TEXTURE_DIM, 
                                                                        G.TEXTURE_DIM],
                                                                width = round((1/3) * G.TEXTURE_DIM),
                                                                height = round((1/3) * G.TEXTURE_DIM))
                        with dpg.tab(label = 'Analysis Tab', 
                                     tag = G.ANALYSIS_TAB_TAG):
                            self.AnalysisView = AnalysisView.AnalysisView()
                
                self.InformationBox = InformationBox.InformationBox(self.VolumeLayerGroups)

        self.VolumeLayerGroups.set_draw_window_dict(self.DrawWindow.window_dict)
        self.VolumeLayerGroups.set_texture_drawlayer_tags(self.DrawWindow.get_texture_drawlayer_tags())
        self.VolumeLayerGroups.set_landmark_drawlayer_tags(self.DrawWindow.get_landmark_drawlayer_tags())
        self.VolumeLayerGroups.get_current_group().set_draw_window_dict(self.DrawWindow.window_dict)
        self.VolumeLayerGroups.get_current_group().set_texture_drawlayer_tags(self.DrawWindow.get_texture_drawlayer_tags())
        self.VolumeLayerGroups.get_current_group().set_landmark_drawlayer_tags(self.DrawWindow.get_landmark_drawlayer_tags())

        self.ImageTools.set_options_panel(self.OptionsPanel)
        self.OptionsPanel.set_volume_and_draw_objects(self.VolumeLayerGroups,
                                                      self.DrawWindow)
        
        self.OptionsPanel.set_info_box(self.InformationBox)
        self.OptionsPanel.set_image_tools(self.ImageTools)
        
        self.InformationBox.set_options_panel(self.OptionsPanel)

        self.FileDialog.initialize(VolumeLayerGroups = self.VolumeLayerGroups,
                                   DrawWindow = self.DrawWindow,
                                   OptionsPanel = self.OptionsPanel,
                                   InformationBox = self.InformationBox,
                                   debug = G.DEBUG_MODE)
        
        
        hover_info = {'mouse_info_text_tag': self.DrawWindow.return_mouse_pos_texture_info_text_tag(self.DrawWindow.get_window_tags()[0]),
                      'Windows': {self.DrawWindow.get_window_tags()[0]: 'view_plane',
                      self.DrawWindow.get_window_tags()[1]: 'view_plane_ortho'}}
        
        dpg.add_item_hover_handler(parent = self.item_hovered_registry, 
                                   user_data = hover_info,
                                   callback = self.OptionsPanel.update_hover_info)
        
        for tag in self.DrawWindow.get_window_tags():
            dpg.bind_item_handler_registry(self.DrawWindow.return_texture_drawlist_tag(tag),
                                           self.item_hovered_registry)
        
        dpg.add_key_press_handler(key = dpg.mvKey_None, 
                                  callback = self.OptionsPanel.mouse_and_keyboard_navigation, 
                                  tag = 'mouse_and_keyboard_navigation_handler', 
                                  parent = self.handler_registry)
        
        self.MenuBar.set_classes(self.VolumeLayerGroups,
                                  self.InformationBox,
                                  self.OptionsPanel,
                                  self.FileDialog,
                                  self.ImageTools,
                                  self.NodeEditor)

    def print_current_tab(self, sender, app_data):
        print('Tab clicked!')
        print('Sender: ', sender)
        print('App Data: ', app_data)

    def _cleanup_(self):
        dict_keys = list(self.__dict__.keys())
        while len(dict_keys) > 0:
            attrib_key = dict_keys.pop()
            try: 
                getattr(self, attrib_key)._cleanup_()
            except:
                pass
            finally:
                setattr(self, attrib_key, None)
                delattr(self, attrib_key)
        
from .Globals import *