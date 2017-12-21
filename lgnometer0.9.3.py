#!/usr/bin/python
#coding=utf-8
import gtk
import vte
import time
import xlwt
import xlrd
import os
import re
import sys

def CtrlCHandler(signum, frame):
    current_time = time.time()
    sys.exit(0)

def show_message(message,title):
    message_dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, None)
    message_dialog.set_markup(message)
    message_dialog.set_title(title)
    message_dialog.run()
    message_dialog.destroy()

#开启脚本用dialog
def begin_response(dialog,response_id):
    if response_id == 1:
        print dialog.get_action_area().get_children()[2].get_text()
    else:
        show_message("The script has exited.","Information")

    dialog.destroy()

def begin():
    begin_dialog = gtk.Dialog()
    begin_dialog_entry = gtk.Entry()

    begin_dialog.add_action_widget(begin_dialog_entry,0)
    begin_dialog.add_button("OK",1)
    begin_dialog.add_button("CANCEL",2)

    begin_dialog.connect("response",begin_response)

    begin_dialog_entry.show()
    begin_dialog.run()

def compare_list_str(x,y):
    z = 0.0
    s = len(x) + len(y)
    #x.sort()
    #y.sort()
    #value = re.compile(r'^[0-9]')
    if len(x) > len(y):
        for i in range(len(y)):
            if y[i] == x[i]:
                z = z + 1
            else:
                if y[i] in x:
                    z = z + 1
                elif len(x[i]) > len(y[i]):
                    if y[i] in x[i]:
                        z = z + float(len(y[i])) / len(x[i])
                elif len(x[i]) < len(y[i]):
                    if x[i] in y[i]:
                        z = z + float(len(x[i])) / len(y[i])
                elif len(x[i]) == len(y[i]):
                    b = 0.0
                    for a in range(len(x[i])):
                        if x[i][a] == y[i][a]:
                            b = b + 1.0 / len(x[i])
                    z = z + b
    else:
        for i in range(len(x)):
            if y[i] == x[i]:
                z = z + 1
            else:
                if x[i] in y:
                    z = z + 1
                elif len(x[i]) > len(y[i]):
                    if y[i] in x[i]:
                        z = z + float(len(y[i])) / len(x[i])
                elif len(x[i]) < len(y[i]):
                    if x[i] in y[i]:
                        z = z + float(len(x[i])) / len(y[i])
                elif len(x[i]) == len(y[i]):
                    b = 0.0
                    for a in range(len(x[i])):
                        if x[i][a] == y[i][a]:
                            b = b + 1.0 / len(x[i])
                    z = z + b        
    result = z / s * 200
    return result


class window:
    def build_excel(self,commands):
        book=xlwt.Workbook()
        sheet=book.add_sheet('results')

        sheet.write(0,0,"server")

        for i in range(0,self.servers.__len__()):
            sheet.write(i + 1,0,self.servers[i])

        for i in range(0,commands.__len__()):
            sheet.write(0,i + 1,commands[i])

        server_num = 0
        for server in self.serverInfo:
            v = self.serverInfo[server]["vTerminal"]
            x,y = v.get_cursor_position()
            content = v.get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
            content = content.split("\n")

            result_lines = []

            line_num = 0
            for line in content:
                for command in commands:
                    if command in line:
                        result_lines.append(line_num)
                line_num = line_num + 1

            result = {}

            command_num = 0
            result_num = result_lines.__len__()
            for command in commands:
                if command_num + 1 == result_num:
                    result[command] = content[result_lines[command_num]:]
                else:
                    result[command] = content[result_lines[command_num]:result_lines[command_num + 1]]
                command_num = command_num + 1

            for i in range(0,commands.__len__()):
#                print result[commands[i]]
                sheet.write(server_num + 1,i + 1,"\n".join(result[commands[i]]))

            server_num = server_num + 1

        book.save("result1.xls")
	show_message("表格创建完成，在当前目录下的result1.xls", "完成")

    def file_choose_dialog(self):
    	filename=None
    	dialog=gtk.FileChooserDialog(title="Select a File", action=gtk.FILE_CHOOSER_ACTION_OPEN,
    	buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    	xls_filter=gtk.FileFilter()
    	xls_filter.set_name("Text files")
    	xls_filter.add_mime_type("xls*")  
    	response = dialog.run()
            
    	if response == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
            dialog.destroy()
	    return filename
    	elif response == gtk.RESPONSE_CANCEL:
            filename = ""
            #print 'Cancel Clicked'
	    dialog.destroy()
            return filename
        dialog.destroy()
	
    def send_log(self,event,server,logtimename=None):
        v = self.serverInfo[server]["vTerminal"]
        x,y = v.get_cursor_position()
        content = self.serverInfo[server]["vTerminal"].get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
        b = gtk.TextBuffer()
        b.set_text(content)
        self.messageView.set_buffer(b)
	#self.save_log(server,logtimename)

    def save_log(self,event,server=None,logtimename=None):
        v = self.serverInfo[server]["vTerminal"]
        x,y = v.get_cursor_position()
        content = v.get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
	todaydir = time.strftime('%Y%m%d',time.localtime())
	if not os.path.exists(todaydir):
	   os.makedirs(todaydir)
        file_object = open(todaydir + "/" + server + "." + logtimename + ".log","w")
        file_object.write(content)
        file_object.close()

    def destroy(self, widget, data=None):
        print "***程序关闭***"
	#self.save_log()
        gtk.main_quit()

    def delete_event(self, widget, event, data=None):
        #self.save_log()
        print "delete event occurred"
        return False

    def exit_terminal(self,event,server):
        #保存该窗口日志并移除该窗口页面与对应的服务器列表项
        #self.save_log(server)

        page_num = self.noteBook.page_num(self.serverInfo[server]["vtebox"])
        self.noteBook.remove_page(page_num)

        self.serverInfo.pop(server)
	self.servers.remove(server)
        #print self.serverInfo
        #没有server了则直接关闭窗口
        #if self.noteBook.get_n_pages() == 0:
        #    self.window.destroy()

    def send_key_event(self,widget,event):
        for server in self.serverInfo:
            if self.serverInfo[server]['checkButton'].get_active():
                v = self.serverInfo[server]["vTerminal"]
                v.do_key_press_event(v,event)
	    
        if event.keyval == gtk.keysyms.Return:
            # x,y = v.get_cursor_position()
            # content = v.get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
            # print content
            widget.set_text("")
        #排除特殊按键的窗口切换，上方向键和tab键
        elif event.keyval == gtk.keysyms.Up:
            return True
        elif event.keyval == gtk.keysyms.Tab:
            widget.set_text("")
            return True

    def copy(self,widget):
        for server in self.serverInfo:
            if self.serverInfo[server]['checkButton'].get_active():
                v = self.serverInfo[server]["vTerminal"]
                v.paste_clipboard()

    def select_Server(self,widget,event,pattern,):
        if pattern == 1:#整选
            for key in self.serverInfo:
                self.serverInfo[key]['checkButton'].set_active(True)
        elif pattern == 2:#反选
            for key in self.serverInfo:
                if self.serverInfo[key]['checkButton'].get_active():
                    self.serverInfo[key]['checkButton'].set_active(False)
                else:
                    self.serverInfo[key]['checkButton'].set_active(True)
        elif pattern ==3:
            def get_response(dialog,response_id):
                if response_id == 1:
                   chsvrs = dialog.get_action_area().get_children()[2].get_text()
                   chsvrlist = chsvrs.split(" ")
                   for key in self.serverInfo:
                      if self.serverInfo[key]["serverName"] in chsvrlist:
                         self.serverInfo[key]['checkButton'].set_active(True)
                      else:
                         self.serverInfo[key]['checkButton'].set_active(False)
                else:
                    #show_message("The script has exited.","Information")
                    dialog.destroy()

            begin_dialog = gtk.Dialog()
            begin_dialog_entry = gtk.Entry()

            begin_dialog.set_title("请输入要选择的对象,空格隔开")
            begin_dialog.add_action_widget(begin_dialog_entry,0)
            begin_dialog.add_button("OK",1)
            begin_dialog.add_button("CANCEL",2)

            begin_dialog.connect("response",get_response)

            begin_dialog_entry.show()
            begin_dialog.run()

    def get_Addresponse(self,dialog,response_id,loginid='None',defcmd='N'):
        
        if response_id == 1:
           #print dialog.get_content_area().get_children()
           #server_string = dialog.get_action_area().get_children()[2].get_text()
           server_string = dialog.get_content_area().get_children()[1].get_text()
           #print server_string
           #print dialog.get_content_area().get_children()[2].get_active()
           servers = server_string.split(" ")
	   #defcmd = 'Y'
           for server in servers:
               if server in self.servers:
                   print server + " 重复了，无法开启多一个窗口，请别名，例如: " + svr + "_1"
                   continue
               else:
                   self.servers.append(server)

		   labbox = gtk.HBox(False, 0)
	           labbox.show()
                   checkButton = gtk.CheckButton()
                   checkButton.set_active(True)
	           checkButton.show()
	    
	           labbox.pack_start(checkButton)
	    
	           vlabel = gtk.Label(server)
	           vlabel.show()
	           labbox.pack_start(vlabel)
		   if dialog.get_content_area().get_children()[2].get_active():
                       if dialog.get_content_area().get_children()[3].get_text() == None:
                           defcmd = 'Y'
                       else:
                           loginid = dialog.get_content_area().get_children()[3].get_text()
                           #print loginid
                           defcmd = 'N'
                   else:
                       defcmd = 'Y'
                   acvtebox = self.cvtebox(loginid,defcmd,server,checkButton)    
                   self.noteBook.append_page(acvtebox,labbox)

                   self.noteBook.show_all()

        else:
            #show_message("The script has exited.","Information")
            dialog.destroy()


    def cvtebox(self,loginid='None',defcmd='N',server=None,checkButton=None):
        vtebox = gtk.VBox(False, 0)
	vtebox.show()
	vtesw = gtk.ScrolledWindow()
        vtesw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        vTerminal = vte.Terminal()
        vTerminal.set_emulation("xterm")

        self.serverInfo[server] = {
                "serverName":server,
                "vTerminal":vTerminal,
                "checkButton":checkButton,
	        "information":"",
		"vtebox":vtebox
        }
	
        redhatver = open("/etc/redhat-release","r").read().split(" ")[-2].split(".")[0]

        if int(redhatver) < 7:
            vTerminal.fork_command()
        else:
            vTerminal.fork_command("/usr/bin/sh")
        

	if defcmd == 'Y' or defcmd == 'y' or defcmd == 'yes':
           pass
	else:
	   vTerminal.feed_child("ssh " + loginid +"@" + server + "\n")
            
	#change color
	fgcolor = gtk.gdk.color_parse('#000000')
        bgcolor = gtk.gdk.color_parse('#ffffff')
        colors =['#2e3436','#cc0000','#4e9a06','#c4a000','\
#3465a4','#75507b','#06989a','#d3d7cf','#555753','#ef2929','#8ae234','#fce94f','\
#729fcf','#ad7fa8','#34e2e2','#eeeeec']
        palette = []
        for color in colors:
           if color:
              palette.append(gtk.gdk.color_parse(color))
        vTerminal.set_colors(fgcolor, bgcolor, palette)
	#change color
        vTerminal.set_size_request(600,400)
        vTerminal.set_scrollback_lines (100000)
	logtimename = time.strftime('%Y%m%d%H%M',time.localtime())
        vTerminal.connect ("contents-changed", self.save_log,server,logtimename)
        vTerminal.connect ("child-exited", self.exit_terminal,server)#contents-changed
        vTerminal.set_scroll_on_output(False)
	   
	vtesw.add(vTerminal)
	vtesw.show
        vtebox.pack_start(vtesw)
	return vtebox

    def add_Server(self,widget,event):
        begin_dialog = gtk.Dialog()
        
        """
        begin_dialog.add_action_widget(begin_dialog_entry,0)
        begin_dialog.add_button("OK",1)
        begin_dialog.add_button("CANCEL",2)
        """
        
        begin_dialog.set_title("添加窗口")
        #begin_dialog.add_action_widget(begin_dialog_entry, 0)

        begin_dialog_label = gtk.Label("请输入要添加的窗口名")
        begin_dialog.vbox.pack_start(begin_dialog_label, False, False, 0)
        begin_dialog_label.show()

        begin_dialog_entry = gtk.Entry()
        begin_dialog.vbox.pack_start(begin_dialog_entry, True, True, 0)
        begin_dialog_entry.show()

        begin_dialog_in_ssh_ck = gtk.CheckButton("以ssh开始")
        begin_dialog.vbox.pack_start(begin_dialog_in_ssh_ck, False, False, 0)
        begin_dialog_in_ssh_ck.show()

        begin_dialog_entry = gtk.Entry()
        begin_dialog_entry.set_text("如果ssh，请填入ID")
        begin_dialog.vbox.pack_start(begin_dialog_entry, False, False, 0)
        begin_dialog_entry.show()

        begin_dialog.add_button("OK",1)
        begin_dialog.add_button("CANCEL",2)
        
        begin_dialog.connect("response",self.get_Addresponse,loginid,defcmd)

        #begin_dialog_entry.show()
        begin_dialog.run()

    def create_Excel(self,widget,event):
        begin_dialog = gtk.Dialog()
        begin_dialog.set_title("生成表格")
	
        table = gtk.Table(20,200)
        table.column_num = 1


        lbl1 = gtk.Label("截取点关键字")
        entry1 = gtk.Entry()
        button = gtk.Button("添加")

        def test(widget):
            lbl = gtk.Label("截取点关键字")
            entry = gtk.Entry()

            lbl.show()
            entry.show()

            start_row = table.column_num*5 + 1
            end_row = table.column_num*5 + 5

            table.attach(lbl,0,10,start_row,end_row)
            table.attach(entry,11,20,start_row,end_row)

            table.column_num = table.column_num + 1
            pass

        def get_Excelcommand(dialog,response_id):
            if response_id == 1:
                result = []
                table_children = table.get_children()
                for child in table_children:
                    if isinstance(child,gtk.Entry):
                        result.append(child.get_text())

                result.reverse()#反转
                self.build_excel(result)
            else:
                pass
            dialog.destroy()


        button.connect("clicked",test)

        lbl1.show()
        entry1.show()
        button.show()

        table.attach(lbl1,0,10,0,5)
        table.attach(entry1,11,20,0,5)
        table.attach(button,11,20,196,200)

        table.show()

        begin_dialog.get_content_area().pack_start(table)
        begin_dialog.add_button("OK",1)
        begin_dialog.add_button("CANCEL",2)

        begin_dialog.connect("response",get_Excelcommand)

        begin_dialog.run()

        pass

    def load_information(self,widget,event):
	filename = self.file_choose_dialog()
	#show_message("文件名为" + filename,"测试")
        if filename =="":
            return
        try:	       
           book=xlrd.open_workbook(filename)
		   		  
	   sh=book.sheet_by_index(0)
           servers = sh.col_values(0)
           target = sh.col_values(1)

           num = 0
           for server in servers:
              if self.serverInfo.has_key(server):
                 self.serverInfo[server]["information"] = target[num]
              num = num + 1

           for server in self.serverInfo:
	      if self.serverInfo[server]["information"] == "":
	         print self.serverInfo[server]["serverName"] + " not found in " + filename
	      else:
	         self.serverInfo[server]["vTerminal"].feed_child(self.serverInfo[server]["information"])
	except (IOError),x:
	   show_message("未知错误发生", "错误")	
        
    def put_servertitle(self,widget,event):
	for server in self.serverInfo:
    	    if self.serverInfo[server]['checkButton'].get_active():
                self.serverInfo[server]["vTerminal"].feed_child(self.serverInfo[server]["serverName"])

    def com_result_bykey(self,widget,base_entry=None):

        base_server = base_entry.get_text()
        result_dict = {}
        if ':' in base_server:
            base_server = base_entry.get_text().split(':')[0]
            cus_keyword = str(base_entry.get_text().split(':')[-1])
        else:
            print "必须填入关键字,如：host1:keyword"
            return 1
        v = self.serverInfo[base_server]["vTerminal"]
        x,y = v.get_cursor_position()
        content = self.serverInfo[base_server]["vTerminal"].get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
        base_list = content.replace(self.serverInfo[base_server]["serverName"],"").replace("# ","").replace("$ ","").split("\n")[0:-1]
        base_list.reverse()
        keylinenum = -9999
        for line in base_list:
            if cus_keyword in line:
                keylinenum = base_list.index(line) + 1
                break
        base_list.reverse()

        if keylinenum != -9999:
            base_content = base_list[-keylinenum:]
            #print base_content
            for server in self.servers:
                if self.serverInfo[server]['checkButton'].get_active() and self.serverInfo[server]["serverName"] != base_server:
                    v = self.serverInfo[server]["vTerminal"]
                    x,y = v.get_cursor_position()
                    content = v.get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
                    last_con_list = content.replace(self.serverInfo[server]["serverName"],"").replace("# ","").replace("$ ","").split("\n")[0:-1]
                    last_con_list.reverse()
                    keylinenum = -9999
                    for line in last_con_list:
                        if cus_keyword in line:
                            keylinenum = last_con_list.index(line) + 1
                            break
                    last_con_list.reverse()
                    if keylinenum != -9999:
                        target_content = last_con_list[-keylinenum:]
                        #print self.serverInfo[server]["serverName"]
                        #print target_content
                        result_dict[server] = round(compare_list_str(base_content,target_content),2)
                    else:
                        result_dict[server] = 0.0
            result_list = []    
            result_list = sorted(result_dict.items(),key=lambda x:x[1],reverse=True)
            
            print "***" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + " 确认结果如下"

            for onere in result_list:
                if onere[-1] < 70.0:
                    if onere[-1] > 50.0:
                        print onere[0],'is \033[1;33m',format(onere[-1],'0.4'),'%\033[0m'
                    else:
                        print onere[0],'is \033[1;31m',format(onere[-1],'0.4'),'%\033[0m'
                else:
                    print onere[0],'is \033[1;32m',format(onere[-1],'0.4'),'%\033[0m'            
        else:
            print "关键字:[" + cus_keyword + "]在" + base_server +"中没有找到,无法进行比较"
                 
    def build_Menu(self):
        menu1 = gtk.Menu()
        menu2 = gtk.Menu()
	menu3 = gtk.Menu()
        menuItem1_1 = gtk.MenuItem("添加窗口")
        menuItem1_2 = gtk.MenuItem("退出")
        menuItem2_1 = gtk.MenuItem("全选")
        menuItem2_2 = gtk.MenuItem("反选")
        menuItem2_3 = gtk.MenuItem("指定选择窗口")
	menuItem2_4 = gtk.MenuItem("输入窗口标题")
        menuItem3_1 = gtk.MenuItem("生成报表")
        menuItem3_2 = gtk.MenuItem("信息载入")
        
        menu1.append(menuItem1_1)
        menu1.append(menuItem1_2)
        menu2.append(menuItem2_1)
        menu2.append(menuItem2_2)
        menu2.append(menuItem2_3)
        menu2.append(menuItem2_4)
        menu3.append(menuItem3_1)
	menu3.append(menuItem3_2)
        
        
        first_menu = gtk.MenuItem("主选单")
        second_menu = gtk.MenuItem("窗口操作")
	third_menu = gtk.MenuItem("表格联动")
        first_menu.set_submenu(menu1)
        second_menu.set_submenu(menu2)
	third_menu.set_submenu(menu3)
	
        menuItem1_1.connect("button-press-event",self.add_Server)	
	menuItem1_2.connect("button-press-event",self.destroy)
        menuItem2_1.connect("button-press-event",self.select_Server,1)
        menuItem2_2.connect("button-press-event",self.select_Server,2)
        menuItem2_3.connect("button-press-event",self.select_Server,3)
	menuItem2_4.connect("button-press-event",self.put_servertitle)
        menuItem3_1.connect("button-press-event",self.create_Excel)
        menuItem3_2.connect("button-press-event",self.load_information)
	
        menu_bar = gtk.MenuBar()
        menu_bar.append (first_menu)
        menu_bar.append (second_menu)
	menu_bar.append (third_menu)

        return menu_bar

    def build_Note(self,loginid='None',defcmd='N'):
        noteBook = gtk.Notebook()
        noteBook.set_tab_pos(gtk.POS_TOP)
        noteBook.set_scrollable(True)
	
        for server in self.servers:
	   labbox = gtk.HBox(False, 0)
	   labbox.show()
           checkButton = gtk.CheckButton()
           checkButton.set_active(True)
	   checkButton.show()
	    
	   labbox.pack_start(checkButton)
	   vlabel = gtk.Label(server)
	   vlabel.show()
	   labbox.pack_start(vlabel)

	   nvtebox = self.cvtebox(loginid,defcmd,server,checkButton)
	   noteBook.append_page(nvtebox,labbox)
        return noteBook


    def build_MessageView(self):
	box1 = gtk.VBox(False, 0)
	box1.set_border_width(1)
	box1.show()
	sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        MessageView = gtk.TextView()

        b = gtk.TextBuffer()
        b.set_text("临时笔记区")

        MessageView.set_buffer(b)
	sw.add(MessageView)
	sw.show()
        MessageView.show()
	
        box1.pack_start(sw)
	
	return box1

    def build_InputEntry(self):
        inputEntry = gtk.Entry()
	inputEntry.set_visibility(False)
        inputEntry.connect("key_press_event",self.send_key_event)
        inputEntry.connect("key_release_event",self.send_key_event)
        inputEntry.connect("paste_clipboard",self.copy)
	
        return inputEntry

    def build_blabel(self,string=None):
	blabel = gtk.Label(string)
	return blabel

    def __init__(self,servers):
        self.servers = servers
        self.serverInfo = {}

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
	self.window.set_title("lgnometer")

        inputEntry = self.build_InputEntry()
        menuBar = self.build_Menu()
	blabel = self.build_blabel("输出确认---》例：基准对象名:[关键字]")
	input_label = self.build_blabel("并行操作->>>")
	versioninfo = self.build_blabel("目前版本0.9.3 alpha")
        
        self.noteBook = self.build_Note(loginid,defcmd)
        self.messageView = self.build_MessageView()

        self.window.set_default_size(800,600)

	main_vbox = gtk.VBox(False, 1)
	main_vbox.set_border_width(1)
        self.window.add(main_vbox)
	main_vbox.show()
        main_vbox.pack_start(menuBar, False, False, 0)
        menuBar.show()
        main_vbox.pack_start(self.noteBook, True, True, 0)
        self.noteBook.show()
        
        com_hbox = gtk.HBox(False, 1)
        com_hbox.pack_start(blabel, False, False, 0)
        blabel.show()
        com_entry = gtk.Entry()
        com_entry.set_text("基准对象名[:关键字]")
        com_hbox.pack_start(com_entry, False, False, 0)
        com_entry.show()
        com_button = gtk.Button("开始输出确认")
        com_button.connect("clicked",self.com_result_bykey,com_entry)
        com_hbox.pack_start(com_button, False, False, 0)
        com_button.show()
        main_vbox.pack_start(com_hbox, False, False, 0)
        com_hbox.show()	

	input_hbox = gtk.HBox(False, 1)
	input_hbox.set_border_width(1)
	input_hbox.pack_start(input_label, False, False, 0)
	input_label.show()
	input_hbox.pack_start(inputEntry, True, True, 0)
	inputEntry.show()
	input_hbox.pack_start(versioninfo, False, False, 0)
	versioninfo.show()
	main_vbox.pack_start(input_hbox, False, False, 0)
	input_hbox.show()

        self.window.show_all()

        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        gtk.main()
        

print "Verion 0.9.3 alpha"
defcmd = raw_input("是否只用shell开始[Y/N]")

if defcmd == 'N' or defcmd == 'NO' or defcmd == 'n' or defcmd == 'no':
    while 1:
        loginid = raw_input("请输入你的登录ID: ")
        if len(loginid) == 0:
           print "***请不要输入空值，再次输入***"
        else:
           break
else:
    loginid = ''

print "***如果输入窗口数多的时候，需按两次回车执行***"

while 1:
    serverlist = raw_input("请输入窗口列表： ")
    if len(serverlist) == 0:
        print "***请不要输入空值，再次输入***"
    else:
        break

serverlist = serverlist.split(" ")
new_svrs = []
for svr in serverlist:
   if svr not in new_svrs:
      if svr != '':
         new_svrs.append(svr)
   else:
      print svr + " 重复了，无法开启多一个窗口，请别名，例如: " + svr + "_1"
try:
   window = window(new_svrs)
except KeyboardInterrupt, e:
   print "!!!警告，你输入了一个ctrl+c指令，为防止错误输入，请看下面"
   endans = raw_input("是否要结束程序?(输入任何按键回车或是无视)")
   if endans != "":
      print "***程序中断***"
      sys.exit()
