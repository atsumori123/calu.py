# Libraries Import
import tkinter as tk

cursor = 3

# 電卓
#-------------------------------------------
# 履歴1～3が選択されたときの処理
#-------------------------------------------
def on_history(no):
	code = var_history[no].get()
	i = code.find('=')
	var_entry.set(code[:i] if i != -1 else code)

	# エントリ行は式のため16進数,10進数,2進数を消去
	var_base['HEX'].set('')
	var_base['DEC'].set('')
	var_base['BIN'].set('')
	entry.icursor(tk.END)

#-------------------------------------------
# 16進数,10進数,2進数が選択されたときの処理
#-------------------------------------------
def on_base(no):
	if no == 0:
		# 16進数が選択されたときの処理
		hex = var_base['HEX'].get()
		if hex != '':
			var_entry.set('0x' + hex.replace(' ', ''))
			entry.icursor(tk.END)

	elif no == 1:
		# 10進数が選択されたときの処理
		dec = var_base['DEC'].get()
		if dec != '':
			var_entry.set(dec.replace(',', ''))
			entry.icursor(tk.END)

	elif no == 2:
		# 2進数が選択されたときの処理
		bin = var_base['BIN'].get()
		if bin != '':
			var_entry.set('0b' + bin.replace(' ', ''))
			entry.icursor(tk.END)

#-------------------------------------------
# メモリーへの退避
#-------------------------------------------
def on_memory(event):
	s = var_entry.get()
	var_mem.set(s)

#-------------------------------------------
# メモリーからの取得
#-------------------------------------------
def on_load():
	s = var_mem.get()
	s = s.replace('\n', '')
	var_entry.set(s)
	entry.icursor(tk.END)

#-------------------------------------------
# 表示の初期化
#-------------------------------------------
def on_clear(event):
	var_entry.set("")
	var_info.set("")
	var_history[0].set('')
	var_history[1].set('')
	var_history[2].set('')
	var_base['HEX'].set('')
	var_base['DEC'].set('')
	var_base['BIN'].set('')

	delete_cursor()

#-------------------------------------------
# カーソルの移動
#-------------------------------------------
def on_cursor_key(event):
	global cursor
	dir = event.keysym
	cursor_table = [history[0], history[1], history[2], entry, base[0], base[1], base[2], mem]

	# 現在のカーソル行の色をデフォルトに戻す
	cursor_table[cursor].config(background=('gray20' if cursor == 3 else BG_COLOR))

	# カーソルを次/前に進める
	cursor += (1 if dir == 'Down' else -1)
	cursor = cursor % 8

	if cursor != 3:
		# 背景色を変更する
		cursor_table[cursor].config(background='darkslateblue')

#-------------------------------------------
# 式が実行可能か検証する
#-------------------------------------------
def is_eval_excutable(code):
	try:
		result = eval(code)
		return True
	except Exception as e:
		return False

#-------------------------------------------
# カーソルの削除
#-------------------------------------------
def delete_cursor():
	global cursor
	cursor_table = [history[0], history[1], history[2], entry, base[0], base[1], base[2], mem]
	cursor_table[cursor].config(background=('gray20' if cursor == 3 else BG_COLOR))
	cursor = 3

#-------------------------------------------
# カーソルキー処理
#-------------------------------------------
def on_cursor():
	global cursor

	# 選択項目を実行
	if cursor >= 0 and cursor <= 2:
		on_history(cursor)
	elif cursor >= 4 and cursor <= 6:
		on_base(cursor - 4)
	elif cursor == 7:
		on_load()

	# カーソル削除
	delete_cursor()

#-------------------------------------------
# 式でEnterキーが押されたときの処理
#-------------------------------------------
def on_enter(event):
	# メッセージクリア
	var_info.set("")

	# カーソル処理
	global cursor
	if cursor != 3:
		on_cursor()
		return

	# 式を取得
	code = var_entry.get()

	# 計算式ではない場合は無効
	if any(word in code for word in ['+', '*', '-', '^', '~']) == False:
		return

	# 式が実行可能か検証
	if is_eval_excutable(code) != True:
		var_info.set("Calculation formula that cannot be executed")
		return

	# 式を実行
	result = eval(code)
	var_entry.set(str(result))

	# 64bitの最上位が1の場合は負の値とする
	if result >= 0x8000000000000000:
		result = ((1<<64) - (result & ((1<<64) - 1))) * -1

	# 式が前回と違うときのみ履歴を更新する
	if var_history[2].get() != "{}={}".format(code, result):
		var_history[0].set(var_history[1].get())
		var_history[1].set(var_history[2].get())
		var_history[2].set("{}={}".format(code, result))
		var_entry.set(str(result))
		entry.icursor(tk.END)

	################
	# 16進数表示
	################
	# step1.数値を16進数文字列に変換して'_'で区切る
	# step2.'_'をスペースに置換し、小文字を大文字に変換
	n = int(result)
	if n < 0:
		# 負の数の場合
		# 負の数を符号拡張のまま扱う
		n = (n & 0xFFFFFFFFFFFFFFFF)

	# 64ビットの範囲を超えた場合（上位ビットを切り捨て）
	n = n & 0xFFFFFFFFFFFFFFFF
	formatted_hex = f"{n:_x}"
	var_base['HEX'].set(formatted_hex.replace('_', ' ').upper())

	################
	# 10進数表示
	################
	formatted_dec = f"{result:,}"
	var_base['DEC'].set(formatted_dec)

	################
	# 2進数表示
	################
	# step1.10進数を2進数に変換し、4桁ごとにアンダースコア '_' で区切る。'b'は2進数（binary）を指定
	# step2.アンダースコアをスペースに置換する
	n = int(result)
	if n >= 0:
		# 正の数の場合
		formatted_bin = f"{n:_b}"
	else:
		# 負の数の場合
		# 32ビットの範囲で表現するための計算
		formatted_bin = f'{(1 << 64) + n:064_b}'
	var_base['BIN'].set(formatted_bin.replace('_', ' '))

################################################################################
#-------------------------------------------
# define
#-------------------------------------------
BG_COLOR	= 'gray13'
FG_COLOR	= 'linen'
FONT		= 'Lucida Console'
PAD_X_L		= 10
PAD_X_R		= 10

#-------------------------------------------
# window setting
#-------------------------------------------
root = tk.Tk()
root.resizable(width=True, height=False)	# 画面サイズを固定
root.title(u"電卓")							# Windowのタイトル
root.geometry("400x350")					# Windowサイズ
root.configure(bg=BG_COLOR)					# GUIの背景色
root.update_idletasks()						# 設定値の更新

##-------------------------------------------
## ショートカットキーの登録
##-------------------------------------------
root.bind('<Escape>',			on_clear)		# 画面のクリア
root.bind('<Alt-KeyPress-m>',	on_memory)		# メモリーへの退避
root.bind('<Up>',				on_cursor_key)	# カーソルの移動
root.bind('<Down>',				on_cursor_key)	# カーソルの移動

#-------------------------------------------
# 動的変数の定義
#-------------------------------------------
var_history	= [tk.StringVar(), tk.StringVar(), tk.StringVar()] # 履歴1～3用
var_base	= {'HEX':tk.StringVar(), 'DEC':tk.StringVar(), 'BIN':tk.StringVar()}
var_entry	= tk.StringVar() # 計算式用
var_mem		= tk.StringVar()
var_info	= tk.StringVar()

#-------------------------------------------
# gridでウィジェットの配置
#-------------------------------------------
row_offset = 0
lbl_col0 = tk.Label(root, text = "0", fg=BG_COLOR, bg=BG_COLOR, width=1)
lbl_col1 = tk.Label(root, text = "1", fg=BG_COLOR, bg=BG_COLOR)
lbl_col0.grid(row=row_offset, column = 0, padx=(PAD_X_L,PAD_X_R))
lbl_col1.grid(row=row_offset, column = 1)
#lbl_col0.grid_forget()	# 非表示
#lbl_col1.grid_forget()	# 非表示
row_offset+=1

#-------------------------------------------
# 履歴の配置
#-------------------------------------------
history = [0, 0, 0]
for i in range(0, 3):
	history[i] = tk.Label(root, textvariable=var_history[i], font=(FONT,10), fg=FG_COLOR, bg=BG_COLOR, anchor='e')
	history[i].grid(row=row_offset, column=0, columnspan=2, sticky='ew', padx=(PAD_X_L,PAD_X_R), pady=5)
	row_offset+=1

#-------------------------------------------
# 式の配置
#-------------------------------------------
entry = tk.Entry(root, textvariable=var_entry, font=(FONT,20), justify=tk.RIGHT,\
			insertbackground="gray80", relief=tk.FLAT, fg=FG_COLOR, bg="gray20")
entry.grid(row=row_offset, column=0, columnspan=2, sticky='ew', padx=(PAD_X_L,PAD_X_R), pady=15, ipady=10)
entry.bind('<Return>', on_enter)
row_offset+=1

# フォーカスを計算式に設定
entry.focus_set()

#-------------------------------------------
# 基数(16進数,10進数,2進数)の配置
#-------------------------------------------
base = [0, 0, 0]
base_table = ['HEX', 'DEC', 'BIN']
for i in range(0, len(base_table)):
	base_label = tk.Label(root, text=base_table[i]+':', font=(FONT,10), fg=FG_COLOR, bg=BG_COLOR)
	base_label.grid(row=row_offset, column=0, padx=(PAD_X_L,PAD_X_R), pady=5)
	base[i] = tk.Label(root, textvariable=var_base[base_table[i]], font=(FONT,10), fg=FG_COLOR, bg=BG_COLOR, anchor='e')
	base[i].grid(row=row_offset, column=1, sticky='ew', padx=(0,PAD_X_R), pady=5)
	row_offset+=1

#-------------------------------------------
# メモリーの配置
#-------------------------------------------
mem_label = tk.Label(root, text='M  :', font=(FONT,10), fg=FG_COLOR, bg=BG_COLOR)
mem_label.grid(row=row_offset, column=0, padx=(PAD_X_L,PAD_X_R), pady=5)
mem = tk.Label(root, textvariable=var_mem, font=(FONT,10), fg=FG_COLOR, bg=BG_COLOR, anchor='e', justify=tk.RIGHT)
mem.grid(row=row_offset, column=1, sticky='ew', padx=(0,PAD_X_R), pady=5)
row_offset+=1

#-------------------------------------------
# メッセージ
#-------------------------------------------
# メッセージの配置
info = tk.Label(root, textvariable=var_info, font=(FONT,10), fg=FG_COLOR, bg=BG_COLOR, anchor='e')
info.grid(row=row_offset, column=0, columnspan=2, sticky='ew', padx=(PAD_X_L,PAD_X_R), pady=10)
row_offset+=1

#--------------------------------------------------------
# ウィンドウのリサイズに合わせてEntryの幅(column=1)を広げる
root.grid_columnconfigure(1, weight=1)

#-------------------------------------------
# Display
#-------------------------------------------
root.mainloop()

