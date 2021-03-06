import copy
import game_data
import game_dialogs
import game_ui
import math
import os
import random as rd
import tkinter as tk
#import winsound as ws



class AAB:
	def __init__(self, parent, *arg, **kwarg):
		self.parent = parent
		self.parent.title("Anhero of Amporal Belitz")
		self.parent.geometry("800x600")
		self.parent.resizable(0, 0)
		center(self.parent, 0, -35)
		self.mainframe = tk.Frame(self.parent, highlightthickness=0, bd=0)
		self.mainframe.pack()
		self.cn = tk.Canvas(self.mainframe, width=800, height=600, bg="black",
			highlightthickness=0, bd=0, cursor="target")
		self.cn.pack()
		# init game data
		self.load_resources()
		self.load_fonts()
		self.load_variables()
		self.load_game_data()
		self.load_basic_ui()
		# test functions
	
	
	def check_quests(self, *args):
		# check quest conditions to adv stage
		aktivq = []
		inv = self.characters["THE_PLAYER"]["inventory"]
		for k, v in self.quests.items():  # find active quests
			qstage = self.quests[k]["stage"][0]
			if (0 < qstage < self.quests[k]["stage"][1]):
				aktivq.append(k)
		for q in aktivq:  # check conditions to adv stage
			stage_now = self.quests[q]["stage"][0]
			req2adv = self.quests[q]["stage{}".format(stage_now)][1]
			hasreq = []  # boolean list to check if requirements met
			for req in req2adv:
				condition = req.split("|")
				if condition[0] == "item":
					if condition[2] == "*":  # already met
						hasreq.append(True)
						continue  # skip to next iteration
					if condition[1] in inv:
						inv.remove(condition[1])
						# update quest data
						reqn = "item|{}|*".format(condition[1])
						req2adv[req2adv.index(req)] = reqn
						hasreq.append(True)
					else: hasreq.append(False)
				elif condition[0] == "reward":
					if condition[1] == "collected": hasreq.append(True)
					else: hasreq.append(False)
			if False not in hasreq: self.quests[q]["stage"][0] += 1
		
	
	def give_reward(self, quest_name, *args):
		p = self.characters["THE_PLAYER"]
		reward = self.quests[quest_name]["reward"]
		p["stats"][5] += reward[0]  # exp, scale later
		p["coin"] += reward[1]
		p["inventory"] += reward[2]  # items
		
		
	def load_basic_ui(self, *args):
		self.load_map(self.current_region)
		# create player image on map and set movement
		self._mimg(500, 195, self.characters["THE_PLAYER"]["map_image"],
			"map_player", "center")	
		self.cn.bind("<Button-1>", self._interact)
		self._mimg(2, 547, "chr_ava-50x50", "btn_Avatar")
		self._mbtn(54, 558, "Lurco", None, w=76, h=38, font=(self.fn[0], 14), txty_change=5)
		self._mbtn(54+(1*79), 558, "Perks", None, w=76, h=38, font=(self.fn[0], 14), txty_change=5)
		self._mbtn(54+(2*79), 558, "Quest", None, w=76, h=38, font=(self.fn[0], 14), txty_change=5)
		self.cn.tag_bind(self._m("btn_Quest"), "<Button-1>", self.start_quest)
		self.cn.tag_bind(self._m("btn_Lurco"), "<Button-1>", lambda _=1: self.start_player_inv())
		self.cn.tag_bind(self._m("btn_Perks"), "<Button-1>", lambda _=1: self.start_perks())
		self._mbtn(54+(3*79), 558, "Map", None, w=76, h=38, font=(self.fn[0], 14), txty_change=5)
		#self._mbtn(60, 545, "Inventory", None)
		self.cn.tag_bind(self._m("btn_Avatar"), "<Button-1>",
			lambda _=1: self.start_dialog("A00"))
	
	
	def load_fonts(self, *args):
		self.fn = [
			"Book Antiqua", "Segoe UI"
		]
		self.fs = [
			12, 11
		]
		self.ftheme = [
			("Book Antiqua", 12),
			("Book Antiqua", 12, "bold"),
			("Segoe UI", 11),
			("Segoe UI", 11, "bold"),
			("Book Antiqua", 17),
		]
	
	
	def load_game_data(self, *args):
		self.characters = game_data.characters
		self.containers = game_data.containers
		self.dialogs = game_dialogs.dialogs
		self.items = game_data.items
		self.map = game_data.map
		self.map_places = {}
		self.perks = game_data.perks
		self.quests = game_data.quests
		self.aktivql = ["A00"]  # current active quests
		self.fertigql = []  # current completed quests
		# places
		# quests
		self.weapon_stats = {
			# HC, IA, CC, CD
			"sword": [80, 0, 20, 1.5],
			"axe": [70, 10, 15, 2.0],
			"mace": [60, 50, 10, 2.5],
		}
		
	
	def load_map(self, map, *args):
		self._mimg(0, 0, self.map[map]["image"], ("map_obj"))
		for k, v in self.map[map]["places"].items():
			n = self.map[map]["places"][k]
			self.placemarker(n["coords"][0], n["coords"][1],
				n["name"], n["map_image"],
				lambda _=1, k=k: self.start_place(k), k)
	
	
	def load_resources(self, *args):
		floc = "resources\\"  # file location of the Gif images
		fdata = os.listdir(floc)  # get all files in the directory
		# separate GIFs from the rest and gives the filename location
		glist = [data[:-4] for data in fdata if data[-4:] == ".gif"]  # Gif
		llist = [floc + data for data in fdata if data[-4:] == ".gif"]  # path
		self.rsc = {}
		for gif in range(len(glist)):
			self.rsc[glist[gif]] = tk.PhotoImage(file = llist[gif])
	
	
	def load_variables(self, *args):
		self.aktiv_caUI = False
		self.aktiv_ui = False
		self.current_region = "Badlands"
		self.in_battle = False
		self.mapicon_t = None  # placemarker hover t
		self.hvrt = None  # btn hover id
		self.map_move = None
		self.mtag = "mainUI"  # main tag of the game
	
	
	def placemarker(self, x, y, place_name, image,
		evts=None, tag=None, x_add=0, y_add=0, *args):
		tag = tag if tag != None else place_name
		tag = "w-{}".format(tag)
		def _phover(mode="enter", *args):
			tn = self._m(tag+"_image")
			i2 = image[:image.index("-")] + "O" + image[image.index("-"):]
			if self.mapicon_t != None:
				self.parent.after_cancel(self.mapicon_t)
				self.mapicon_t = None
			if mode == "enter":
				self.mapicon_t = self.parent.after(150,
					lambda _=1: self.cn.itemconfigure(tn, image=self.rsc[i2]))
			else:
				self.cn.itemconfigure(tn, image=self.rsc[image])
		h = int(image[-2:])  # height 99px max
		add = (h / 2) + 12
		self._mimg(x, y, image, ("map_obj", tag, tag+"_image"), "center")
		self._mtxt(x+x_add, y-add, place_name, ("map_obj", tag, tag+"_txt"),
			anchor="center", font=(self.fn[0], self.fs[1]), fill="#441122")
		self.map_places[self._m(tag)] = evts
		self.cn.tag_bind(self._m(tag), "<Enter>", lambda _=1: _phover())
		self.cn.tag_bind(self._m(tag), "<Leave>", lambda _=1: _phover("l"))
	
	
	def raise_ctags(self, *args):
		a = ["Avatar", "Lurco", "Perks", "Quest", "Map"]
		for i in range(len(a)):
			tag = self._m("btn_{}".format(a[i]))
			self.cn.tag_raise(tag)
	
	
	def start_battle(self, enemy, paths=None, player="THE_PLAYER", *args):
		def end_fight(paths, *args):
			self._uistatus("inaktiv")
			#self.disable_cm(0)
			#self.in_battle = False
			# paths: 3 functions for win, defeat, flee. respectively. 0, 1, 2
			self.battle_result = self.cn.itemcget("battle_result", "text")
			self.cn.delete("battle_ui", "battle_result")
			self.characters[player] = copy.deepcopy(sc.player)
			#self.char[player]["coin"] += copy.deepcopy(sc.enemy["coin"])
			if paths != None:
				if "Victory" in self.battle_result:
					self.start_dialog(paths[0])
					# temp 
					#self.dialog[paths[0]]["rewards"][1] = self.scale_exp(self.dialog[paths[0]]["rewards"][1])
					self.characters[player]["stats"][5] += self.dialog[paths[0]]["rewards"][1]
					self.characters[player]["coin"] += self.dialog[paths[0]]["rewards"][0]
				elif "Defeat" in self.battle_result:
					x = rd.randint(0, 10)
					if x <= 5:
						self.start_dialog(paths[2])
					else:
						self._mimg(0, 0, "aBg1")
						self.start_dialog(paths[1])
				elif "Flee" in self.battle_result:
					self.start_dialog(paths[2])
				else:
					pass
					#print self.battle_result
		#self.cn.delete("dialogUI")
		#sc = aBtl1.Battle(self.parent, self.cn, self.e["AnEncounterOnTheRoad-FleePass"])
		'''
		sc = aBtl1.Battle(self.parent, self.cn, lambda: end_fight(
			[self.e["AnEncounterOnTheRoad-FightPass"], 
			self.e["AnEncounterOnTheRoad-FightFail"],
			self.e["AnEncounterOnTheRoad-FleePass"]]))
		sc.battle("The Player", "Brigands0")
		'''
		sc = game_ui.Battle(self, self.cn, self.characters[player], self.characters[enemy], 
			lambda _=1: end_fight(paths))
		self._uistatus("aktiv")
		#self.disable_cm()
		self.cn.delete("caUI")
		#self.in_battle = True
	
	
	def start_dialog(self, dialog_id, extract=None, *args):
		def lv_(s=0, *args):
			if s == 0:
				try: self.go_place.aktiv_ui = True
				except: pass
				self.parent.after(100, lambda _=1: lv_(1))
			else:
				try: self.go_place.aktiv_ui = False
				except: pass
		def end_dialog():
			self._uistatus("inaktiv")
			lv_()
			if extract is not None:
				extract()
		if not self.aktiv_caUI:
			try: self.go_place.aktiv_ui = True
			except: pass
			self._uistatus("aktiv")
			self.check_quests()
			self.go_dialog = game_ui.Dialogs(self, dialog_id, end_dialog)
	
	
	def start_perks(self, party1="THE_PLAYER", extract=None, override=False, *args):
		def lv_(s=0, *args):
			if s == 0:
				try: self.go_place.aktiv_ui = True
				except: pass
				self.parent.after(100, lambda _=1: lv_(1))
			else:
				try: self.go_place.aktiv_ui = False
				except: pass
		def end_perkbox(*args):
			self.aktiv_caUI = False
			self._uistatus("inaktiv")
			lv_()
			if extract is not None:
				extract()
		def perksg1(*args):
			# copy to not mix values with real ones.
			self.characters[party1] = copy.deepcopy(self.go_perks.p1data)
			self.perks = copy.deepcopy(self.go_perks.perksl)
			for i in range(len(self.characters[party1]["stats"])):
				if i == 0:
					a = float(self.characters[party1]["stats"][i][0])
					b = float(self.characters[party1]["stats"][i][1])
					self.characters[party1]["stats"][i][0] = round(a, 1)
					self.characters[party1]["stats"][i][1]= round(b, 1)
				elif i in [5, 9]:
					self.characters[party1]["stats"][i] = int(self.characters[party1]["stats"][i])
				else:
					n = float(self.characters[party1]["stats"][i])
					self.characters[party1]["stats"][i] = round(n, 1)
			for k, v in self.characters[party1]["mods"].items():
				for x in range(len(v)):
					v[x] = round(v[x], 1)
		if not self.aktiv_caUI or override == True:
			self.aktiv_caUI = True
			try: self.go_place.aktiv_ui = True
			except: pass
			self._uistatus("aktiv")
			self.cn.delete("caUI")
			self.aktiv_caUI = True
			self.go_perks = game_ui.Perks(self, self.characters[party1], end_perkbox, perksg1)
	
	
	def start_place(self, place, extract=None, startxy=None, *args):
		def end_place():
			self._uistatus("inaktiv")
			self.cn.bind("<Button-1>", self._interact)
			if extract is not None: extract()
		self.check_quests()	
		self._uistatus("aktiv")
		self.go_place = game_ui.Places(self, place, end_place, startxy)
	
	
	def start_player_inv(self, extract=None, *args):
		def lv_(s=0, *args):
			if s == 0:
				try: self.go_place.aktiv_ui = True
				except: pass
				self.parent.after(100, lambda _=1: lv_(1))
			else:
				try: self.go_place.aktiv_ui = False
				except: pass
		def end_player_inv():
			self.aktiv_caUI = False
			self._uistatus("inaktiv")
			self.characters["THE_PLAYER"] = self.go_inv.p1data
			lv_()
			if extract is not None:
				extract()
		if not self.aktiv_caUI:
			self.aktiv_caUI = True
			try: self.go_place.aktiv_ui = True
			except: pass
			self._uistatus("aktiv")
			self.go_inv = game_ui.Inventory(self, end_player_inv)
			
	
	def start_quest(self, *args):
		def end_quest():
			self._uistatus("inaktiv")
			self._caUIstatus("inaktiv")
			#lv_()
			#if extract is not None:
			#	extract()
		#try: self.go_place.aktiv_ui = True
		#except: pass
		self._uistatus("aktiv")
		self.aktiv_caUI = True
		#self.check_quests()
		self.go_quest = game_ui.Quests(self, end_quest)
	
	
	def start_store(self, merchant, extract=None, bg=None, *args):
		def end_store(*args):
			#self.disable_cm(0)
			self.cn.delete(self._m("str_bg"))
			self.characters["THE_PLAYER"] = self.go_store.pdata
			if extract is not None:
				extract()
		if not self.aktiv_caUI:
			#self.disable_cm()
			self.check_quests()
			if bg is not None: self._mimg(0, 0, bg, "str_bg")
			self.go_store = game_ui.Stores(self, merchant, end_store)
	
	
	def start_tradebox(self, container, extract=None, bg=None, *args):
		def end_tradebox(*args):
			#self.disable_cm(0)
			self.cn.delete(self._m("trd_bg"))
			self.characters["THE_PLAYER"] = self.go_tradebox.pdata
			self.containers[container] = self.go_tradebox.cdata
			if extract is not None:
				extract()
		if not self.aktiv_caUI:
			#self.disable_cm()
			self.check_quests()
			if bg is not None: self._mimg(0, 0, bg, "trd_bg")
			self.go_tradebox = game_ui.Tradebox(self, container, end_tradebox)
	
	
	def _check_tags(self, tags):
		# Input: ("a", "b")
		# Output: (mtag, "mtag_a", "mtag_b")
		if tags is None:
			tags = self.mtag
		elif isinstance(tags, str):  # string
			x = [self._m(tags)]
			tags = tuple([self.mtag] + x)
		else:
			x = []
			for i in tags:
				x.append(self._m(i))
			tags = tuple([self.mtag] + x)
		return tags
		
		
	def _interact(self, event, *args):
		id_num = self.cn.find_closest(event.x, event.y)[0]
		id_tags = self.cn.gettags(id_num)
		if self._m("map_obj") in id_tags and self.aktiv_ui is False:
			if self.map_move is not None:
				self.parent.after_cancel(self.map_move)
				self.map_move = None
			# calculate variables
			coords = self.cn.coords(self._m("map_player"))
			px, py = coords[0], coords[1]
			lx, ly = event.x, event.y
			x, y = lx-px, ly-py
			dist = math.sqrt(abs(x)**2 + abs(y)**2)
			steps = dist / 1.75  # player speed 5.0 max
			ax = x / steps
			ay = y / steps
			evt = None
			for i in id_tags:
				txt = "{}_w-".format(self.mtag)
				try:
					if i[:len(txt)] == txt:
						evt = self.map_places[i]
						break
				except:
					print("_interact error")
			self._move2loc(ax, ay, steps, evt)
	
	
	def _m(self, tag):
		return "{}_{}".format(self.mtag, tag)
	

	def _mbtn(self, x1, y1, text, command, font=None, w=None, h=None,
		bg="#776611", txty_change=0, *args):
		w = w if w is not None else 4 + (9 * len(text))
		h = 25 if h is None else h
		tag = "btn_{}".format(text)
		def _bhover(mode="enter", *args):
			tn = self._m(tag+"_rect")
			if self.hvrt != None:
				self.parent.after_cancel(self.hvrt)
				self.hvrt = None
			if mode == "enter":
				self.hvrt = self.parent.after(100,
					lambda _=1: self.cn.itemconfigure(tn, fill="orange"))
			else: self.cn.itemconfigure(tn, fill=bg)
		self._mrect(x1, y1, w, h, bg, (tag, tag+"_rect"), "black", 2)
		x2, y2 = x1 + (w / 2) - 1, y1 + 1
		self._mtxt(x2, y2+txty_change, text, (tag, tag+"_txt"), font=font,
			anchor=tk.N, width=w)
		if command is not None:
			self.cn.tag_bind(self.m(tag), "<Button-1>", lambda _=1: command())
		#ntag = self._m(tag+"_txt")
		ntag = self._m(tag)
		self.cn.tag_bind(ntag, "<Enter>", lambda _=1: _bhover())
		self.cn.tag_bind(ntag, "<Leave>", lambda _=1: _bhover("l"))
	
	
	def _mimg(self, x, y, image, tags=None, anchor=tk.NW, *args):
		tags = self._check_tags(tags)  # must be tuple
		self.cn.create_image(x, y, image=self.rsc[image], tags=tags,
			anchor=anchor)
	
	
	def _move2loc(self, x_add, y_add, steps, evt=None, *args):
		if steps >= 0 and self.aktiv_ui is False:
			self.cn.move(self._m("map_player"), x_add, y_add)
			steps -= 1
			self.map_move = self.parent.after(50, lambda _=1: 
				self._move2loc(x_add, y_add, steps, evt))
		elif steps < 0:
			self.map_move = None
			if evt is not None:
				evt()
	

	def _mrect(self, x1, y1, w, h, fill="black", tags=None, c=None, width=0):
		tags = self._check_tags(tags)  # must be tuple
		self.cn.create_rectangle(x1, y1, x1+w, y1+h, fill=fill, tags=tags,
			outline=c, width=width)
	
		
	def _mtxt(self, x, y, txt, tags=None, font=None, anchor=tk.NW,
		fill="black", width=250, align="left", *args):
		tags = self._check_tags(tags)  # must be tuple
		font = (self.fn[0], self.fs[0]) if font is None else font
		self.cn.create_text(x, y, text=txt, tags=tags, font=font,
			anchor=anchor, fill=fill, width=width, justify=align)

	
	def _caUIstatus(self, state, *args):
		if state == "aktiv":
			self.aktiv_caUI = True
		elif state == "inaktiv":
			self.aktiv_caUI = True
			self.parent.after(100, lambda _=1: self._caUIstatus("2inaktiv"))
		elif state == "2inaktiv":  # prevents moving immediately
			self.aktiv_caUI = False	
			
	
	def _uistatus(self, state, *args):
		if state == "aktiv":
			self.aktiv_ui = True
		elif state == "inaktiv":
			self.aktiv_ui = True
			self.parent.after(100, lambda _=1: self._uistatus("2inaktiv"))
		elif state == "2inaktiv":  # prevents moving immediately
			self.aktiv_ui = False
			
	
def center(win, x_add=0, y_add=0):
	win.update_idletasks()
	width = win.winfo_width()
	height = win.winfo_height()
	x = (win.winfo_screenwidth() // 2) - (width // 2)
	y = (win.winfo_screenheight() // 2) - (height //2)
	win.geometry("{}x{}+{}+{}".format(width, height, x+x_add, y+y_add))


if __name__ == "__main__":
	root = tk.Tk()
	app = AAB(root)
	root.mainloop()