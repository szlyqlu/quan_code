#!/usr/bin/python
#coding=utf-8
import gtk
import vte
import time
import re
import xlwt
import xlrd
import os

def show_message(message,title):
    message_dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, None);
    message_dialog.set_markup(message);
    message_dialog.set_title(title)
    message_dialog.run();
    message_dialog.destroy()

#开启脚本用dialog
def begin_response(dialog,response_id):
    if response_id == 1:
        print dialog.get_action_area().get_children()[2].get_text();
    else:
        show_message("The script has exited.","Information");

    dialog.destroy();

def begin():
    begin_dialog = gtk.Dialog();
    begin_dialog_entry = gtk.Entry();

    begin_dialog.add_action_widget(begin_dialog_entry,0);
    begin_dialog.add_button("OK",1);
    begin_dialog.add_button("CANCEL",2);

    begin_dialog.connect("response",begin_response);

    begin_dialog_entry.show();
    begin_dialog.run();

class window:
    def build_excel(self,commands):
        book=xlwt.Workbook()
        sheet=book.add_sheet('results')

        sheet.write(0,0,"server")

        for i in range(0,self.servers.__len__()):
            sheet.write(i + 1,0,self.servers[i]);

        for i in range(0,commands.__len__()):
            sheet.write(0,i + 1,commands[i]);

        server_num = 0
        for server in self.serverInfo:
            v = self.serverInfo[server]["vTerminal"]
            x,y = v.get_cursor_position()
            content = v.get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
            content = content.split("\n")

            result_lines = [];

            line_num = 0
            for line in content:
                for command in commands:
                    if command in line:
                        result_lines.append(line_num)
                line_num = line_num + 1

            result = {}

            command_num = 0;
            result_num = result_lines.__len__();
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
	
    def send_log(self,event,server,logtimename=None):
        v = self.serverInfo[server]["vTerminal"]
        x,y = v.get_cursor_position()
        content = self.serverInfo[server]["vTerminal"].get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
        b = gtk.TextBuffer();
        b.set_text(content)
        #self.messageView.set_buffer(b);
	self.save_log(server,logtimename)

    def save_log(self,server=None,logtimename=None):
        if server !=None:
            v = self.serverInfo[server]["vTerminal"]
            x,y = v.get_cursor_position()
            content = v.get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
	    todaydir = time.strftime('%Y%m%d',time.localtime())
	    if not os.path.exists(todaydir):
	        os.makedirs(todaydir)
            file_object = open(todaydir + "/" + server + "." + logtimename + ".log","w")
            file_object.write(content)
            file_object.close()

        else:
            for server in self.serverInfo:
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
        #self.save_log();
        print "delete event occurred"
        return False

    def exit_terminal(self,event,server):
        #保存该窗口日志并移除该窗口页面与对应的服务器列表项
        #self.save_log(server)

        page_num = self.noteBook.page_num(self.serverInfo[server]["vTerminal"])
        self.noteBook.remove_page(page_num)

        self.serverInfo.pop(server)
        #没有server了则直接关闭窗口
        if self.noteBook.get_n_pages() == 0:
            self.window.destroy();

    def send_key_event(self,widget,event):
        for server in self.serverInfo:
            if self.serverInfo[server]['checkButton'].get_active():
                v = self.serverInfo[server]["vTerminal"];
                v.do_key_press_event(v,event)
        if event.keyval == gtk.keysyms.Return:
            # x,y = v.get_cursor_position()
            # content = v.get_text_range(0, 0, y,x,lambda widget, col, row, junk: True)
            # print content
            widget.set_text("")

    def copy(self,widget):
        for server in self.serverInfo:
            if self.serverInfo[server]['checkButton'].get_active():
                v = self.serverInfo[server]["vTerminal"];
                v.paste_clipboard()

    def select_Server(self,widget,event,pattern,):
        if pattern == 1:#整选
            for key in self.serverInfo:
                self.serverInfo[key]['checkButton'].set_active(True);
        elif pattern == 2:#反选
            for key in self.serverInfo:
                if self.serverInfo[key]['checkButton'].get_active():
                    self.serverInfo[key]['checkButton'].set_active(False);
                else:
                    self.serverInfo[key]['checkButton'].set_active(True);
        elif pattern ==3:
            def get_response(dialog,response_id):
                if response_id == 1:
                    regex = dialog.get_action_area().get_children()[2].get_text();
                    for key in self.serverInfo:
                        s = re.match(regex,self.serverInfo[key]['serverName'])
                        print s
                        if s:
                            self.serverInfo[key]['checkButton'].set_active(False);
                        else:
                            self.serverInfo[key]['checkButton'].set_active(True);
                else:
                    show_message("The script has exited.","Information");
                dialog.destroy();

            begin_dialog = gtk.Dialog();
            begin_dialog_entry = gtk.Entry();

            begin_dialog.set_title("请输入筛选的正则表达式")
            begin_dialog.add_action_widget(begin_dialog_entry,0);
            begin_dialog.add_button("OK",1);
            begin_dialog.add_button("CANCEL",2);

            begin_dialog.connect("response",get_response);

            begin_dialog_entry.show();
            begin_dialog.run();

    def get_Addresponse(self,dialog,response_id,loginid='None',defcmd='N'):
        if response_id == 1:
            server_string = dialog.get_action_area().get_children()[2].get_text();
            servers = server_string.split(" ");
            for server in servers:
                if server in self.servers:
                    print "该服务器已存在于列表中"
                    continue
                else:
                    self.servers.append(server);
                checkButton = gtk.CheckButton(server);
                checkButton.set_active(True);
                #vbox.add(checkButton);
	    	vtebox = gtk.VBox(False, 0);
	    	vtebox.show();
	    	vtesw = gtk.ScrolledWindow();
            	vtesw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		
                vTerminal = vte.Terminal();               

                self.serverInfo[server] = {
                        "serverName":server,
                        "vTerminal":vTerminal,
                        "checkButton":checkButton,
                        "information":""
                    }
                vTerminal.fork_command()
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
                vTerminal.set_scrollback_lines (100000)
	        logtimename = time.strftime('%Y%m%d%H%M',time.localtime())
                vTerminal.connect ("contents-changed", self.send_log,server,logtimename)
		vTerminal.connect ("child-exited", self.exit_terminal,server)#contents-changed
                vTerminal.set_scroll_on_output(False);

	    	vtesw.add(vTerminal)
	    	vtesw.show
            	vtebox.pack_start(vtesw)

                self.noteBook.append_page(vtebox,checkButton);
                self.noteBook.show_all()

        else:
            #show_message("The script has exited.","Information");
            dialog.destroy();

    def add_Server(self,widget,event):
        begin_dialog = gtk.Dialog();
        begin_dialog_entry = gtk.Entry();

        begin_dialog.set_title("请输入要添加的窗口名")
        begin_dialog.add_action_widget(begin_dialog_entry,0);
        begin_dialog.add_button("OK",1);
        begin_dialog.add_button("CANCEL",2);

        begin_dialog.connect("response",self.get_Addresponse,loginid,defcmd);

        begin_dialog_entry.show();
        begin_dialog.run();

    def create_Excel(self,widget,event):
        begin_dialog = gtk.Dialog();
        begin_dialog.set_title("生成表格")
	
        table = gtk.Table(20,200);
        table.column_num = 1


        lbl1 = gtk.Label("截取点关键字")
        entry1 = gtk.Entry()
        button = gtk.Button("添加")

        def test(widget):
            lbl = gtk.Label("截取点关键字")
            entry = gtk.Entry()

            lbl.show();
            entry.show();

            start_row = table.column_num*5 + 1;
            end_row = table.column_num*5 + 5;

            table.attach(lbl,0,10,start_row,end_row);
            table.attach(entry,11,20,start_row,end_row);

            table.column_num = table.column_num + 1;
            pass

        def get_Excelcommand(dialog,response_id):
            if response_id == 1:
                result = []
                table_children = table.get_children()
                for child in table_children:
                    if isinstance(child,gtk.Entry):
                        result.append(child.get_text());

                result.reverse();#反转
                self.build_excel(result)
            else:
                pass
            dialog.destroy();


        button.connect("clicked",test)

        lbl1.show()
        entry1.show()
        button.show()

        table.attach(lbl1,0,10,0,5);
        table.attach(entry1,11,20,0,5);
        table.attach(button,11,20,196,200);

        table.show();

        begin_dialog.get_content_area().pack_start(table)
        begin_dialog.add_button("OK",1);
        begin_dialog.add_button("CANCEL",2);

        begin_dialog.connect("response",get_Excelcommand);

        begin_dialog.run();

        pass

    def load_information(self,widget,event):
        try:	       
           book=xlrd.open_workbook("information.xls")
		   		  
	   sh=book.sheet_by_index(0)
           servers = sh.col_values(0)
           target = sh.col_values(1)

           num = 0
           for server in servers:
              if self.serverInfo.has_key(server):
                 self.serverInfo[server]["information"] = target[num]
              num = num + 1;

           for server in self.serverInfo:
	      if self.serverInfo[server]["information"] == "":
	         print self.serverInfo[server]["serverName"] + " not found in ./information.xls."
	      else:
	         self.serverInfo[server]["vTerminal"].feed_child(self.serverInfo[server]["information"])
	except (IOError),x:
	   show_message("在脚本当前目录下没有information.xls文件", "错误")

    def build_Menu(self):
        menu1 = gtk.Menu();
        menu2 = gtk.Menu();
        menuItem1_1 = gtk.MenuItem("添加窗口");
        menuItem1_2 = gtk.MenuItem("退出");
        menuItem2_1 = gtk.MenuItem("全选");
        menuItem2_2 = gtk.MenuItem("反选");
        menuItem2_3 = gtk.MenuItem("正则选择");
        menuItem2_4 = gtk.MenuItem("生成报表");
        menuItem2_5 = gtk.MenuItem("信息载入");
        menu1.append(menuItem1_1)
        menu1.append(menuItem1_2)
        menu2.append(menuItem2_1)
        menu2.append(menuItem2_2)
        menu2.append(menuItem2_3)
        menu2.append(menuItem2_4)
        menu2.append(menuItem2_5)


        first_menu = gtk.MenuItem("主选单")
        second_menu = gtk.MenuItem("服务器操作")
        first_menu.set_submenu(menu1)
        second_menu.set_submenu(menu2)
	
        menuItem1_1.connect("button-press-event",self.add_Server);	
	menuItem1_2.connect("button-press-event",self.destroy);
        menuItem2_1.connect("button-press-event",self.select_Server,1);
        menuItem2_2.connect("button-press-event",self.select_Server,2);
        menuItem2_3.connect("button-press-event",self.select_Server,3);
        menuItem2_4.connect("button-press-event",self.create_Excel);
        menuItem2_5.connect("button-press-event",self.load_information);

        menu_bar = gtk.MenuBar()
        menu_bar.append (first_menu)
        menu_bar.append (second_menu)

        return menu_bar

    def build_Note(self,loginid='None',defcmd='N'):
        noteBook = gtk.Notebook();
        noteBook.set_tab_pos(gtk.POS_LEFT);
        noteBook.set_scrollable(True);
	
        for server in self.servers:
            checkButton = gtk.CheckButton(server);
            checkButton.set_active(True);
            #vbox.add(checkButton)

	    vtebox = gtk.VBox(False, 0);
	    vtebox.show();
	    vtesw = gtk.ScrolledWindow();
            vtesw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

            vTerminal = vte.Terminal();

            self.serverInfo[server] = {
                    "serverName":server,
                    "vTerminal":vTerminal,
                    "checkButton":checkButton,
		    "information":""
                }
            vTerminal.fork_command()

	    if defcmd == 'Y' or defcmd == 'y' or defcmd == 'yes':
              pass
	    else:
	        vTerminal.feed_child("ssh " + loginid +"@" + server + "\n")
            
#	    vTerminal.feed_child("echo ssh "+ loginid +"@" + server)
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
            vTerminal.set_size_request(1000,720)
            vTerminal.set_scrollback_lines (100000)
	    logtimename = time.strftime('%Y%m%d%H%M',time.localtime())
            vTerminal.connect ("contents-changed", self.send_log,server,logtimename)
            vTerminal.connect ("child-exited", self.exit_terminal,server)#contents-changed
            vTerminal.set_scroll_on_output(False);
	    
	    vtesw.add(vTerminal)
	    vtesw.show
            vtebox.pack_start(vtesw)
	    
            noteBook.append_page(vtebox,checkButton);

        return noteBook;

    def build_MessageView(self):
	box1 = gtk.VBox(False, 0);
	box1.set_border_width(1);
	box1.show();
	sw = gtk.ScrolledWindow();
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        MessageView = gtk.TextView();

        b = gtk.TextBuffer();
        b.set_text("临时笔记区")

        MessageView.set_buffer(b);
	sw.add(MessageView);
	sw.show();
        MessageView.show();
	
        box1.pack_start(sw);
	
	return box1

    def build_InputEntry(self):
        inputEntry = gtk.Entry();
	inputEntry.set_visibility(False)
        inputEntry.connect("key_press_event",self.send_key_event)
        inputEntry.connect("key_release_event",self.send_key_event)
        inputEntry.connect("paste_clipboard",self.copy)
	
        return inputEntry;

    def build_blabel(self,string=None):
	blabel = gtk.Label(string);
	return blabel;

    def __init__(self,servers):
        self.servers = servers;
        self.serverInfo = {};

        table = gtk.Table(60,50);
        self.window = gtk.Window();

        inputEntry = self.build_InputEntry();
        menuBar = self.build_Menu();
	blabel = self.build_blabel("并行输入->>>>");
	versioninfo = self.build_blabel("目前版本0.6 alph");
        self.noteBook = self.build_Note(loginid,defcmd);
        self.messageView = self.build_MessageView();

        table.attach(menuBar,0,60,0,10);
        table.attach(self.noteBook,0,50,11,50, gtk.EXPAND, gtk.FILL);
        table.attach(self.messageView, 51, 200, 11, 50);
	table.attach(blabel, 0, 3, 51, 60);
        table.attach(inputEntry,3,40,51,60);
	table.attach(versioninfo,41,60,51,60)

        self.window.set_default_size(1280,800);
        self.window.add(table);
        self.window.show_all();

        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        gtk.main();

print "Verion 0.7 alph"
defcmd = raw_input("是否只用shell开始，配合information.xls可以有妙用[Y/N]")

if defcmd == 'N' or defcmd == 'NO' or defcmd == 'n' or defcmd == 'no':
    while 1:
        loginid = raw_input("请输入你的登录ID: ")
        if len(loginid) == 0:
           print "***请不要输入空值，再次输入***"
        else:
           break
else:
    loginid = ''

print "***如果服务器数多的时候，需按两次回车执行***"

while 1:
    serverlist = raw_input("请输入服务器列表： ")
    if len(serverlist) == 0:
        print "***请不要输入空值，再次输入***"
    else:
        break

serverlist = serverlist.split(" ")

window = window(serverlist);
