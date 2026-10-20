import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_HOST='localhost'
DB_USER='root'
DB_PASSWORD='1234'
DB_NAME='library_db'

def db():
    return mysql.connector.connect(host=DB_HOST,user=DB_USER,password=DB_PASSWORD,database=DB_NAME)

class LibraryApp:
    def __init__(self,root):
        self.root=root; root.title('NEXORA - Smart Library Platform'); root.geometry('1200x700'); root.minsize(1050,650); root.configure(bg='#f4f6f8')
        self.sidebar=tk.Frame(root,bg='#172033',width=220); self.sidebar.pack(side='left',fill='y'); self.sidebar.pack_propagate(False)
        self.content=tk.Frame(root,bg='#f4f6f8'); self.content.pack(side='right',fill='both',expand=True)
        self.create_sidebar(); self.show_dashboard()
    def create_sidebar(self):
        tk.Label(self.sidebar,text='NEXORA',bg='#172033',fg='white',font=('Arial',24,'bold')).pack(pady=(30,3))
        tk.Label(self.sidebar,text='SMART LIBRARY',bg='#172033',fg='#aeb8c8',font=('Arial',9,'bold')).pack(pady=(0,30))
        for t,c in [('Dashboard',self.show_dashboard),('Books',self.show_books),('Members',self.show_members),('Borrow / Return',self.show_borrowing),('Fine Management',self.show_fines),('Analytics',self.show_analytics)]:
            tk.Button(self.sidebar,text=t,command=c,bg='#172033',fg='white',activebackground='#263550',activeforeground='white',relief='flat',anchor='w',padx=25,font=('Arial',11,'bold'),cursor='hand2').pack(fill='x',ipady=12,pady=2)
    def clear(self):
        for w in self.content.winfo_children(): w.destroy()
    def title(self,t,sub=''):
        h=tk.Frame(self.content,bg='#f4f6f8'); h.pack(fill='x',padx=25,pady=(20,10))
        tk.Label(h,text=t,bg='#f4f6f8',fg='#172033',font=('Arial',23,'bold')).pack(anchor='w')
        if sub: tk.Label(h,text=sub,bg='#f4f6f8',fg='#6b7280',font=('Arial',10)).pack(anchor='w')
    def query(self,sql,args=()):
        c=db(); cur=c.cursor(); cur.execute(sql,args); rows=cur.fetchall(); cur.close(); c.close(); return rows
    def show_dashboard(self):
        self.clear(); self.title('Dashboard','Overview of your smart library')
        try:
            fine=self.query("SELECT COALESCE(SUM(amount),0) FROM Fine WHERE payment_status='Unpaid'")[0][0]
            stats=[('Total Books',self.query('SELECT COUNT(*) FROM Books')[0][0]),('Members',self.query('SELECT COUNT(*) FROM Members')[0][0]),('Borrowed',self.query("SELECT COUNT(*) FROM Borrowing WHERE status='Borrowed'")[0][0]),('Returned',self.query("SELECT COUNT(*) FROM Borrowing WHERE status='Returned'")[0][0]),('Unpaid Fine',f'₹{fine:.2f}')]
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e)); return
        f=tk.Frame(self.content,bg='#f4f6f8'); f.pack(fill='x',padx=25)
        for n,v in stats:
            x=tk.Frame(f,bg='white',bd=1,relief='solid'); x.pack(side='left',fill='both',expand=True,padx=5,ipady=10)
            tk.Label(x,text=n,bg='white',fg='#6b7280',font=('Arial',10,'bold')).pack(pady=(10,4)); tk.Label(x,text=str(v),bg='white',fg='#172033',font=('Arial',20,'bold')).pack(pady=(0,10))
        box=tk.Frame(self.content,bg='white',bd=1,relief='solid'); box.pack(fill='both',expand=True,padx=30,pady=20)
        tk.Label(box,text='Recent Borrowing',bg='white',fg='#172033',font=('Arial',16,'bold')).pack(anchor='w',padx=15,pady=12)
        tr=self.tree(box,('ID','Member','Book','Borrow Date','Return Date','Status'),[60,160,250,120,120,100]); tr.pack(fill='both',expand=True,padx=15,pady=(0,15))
        try:
            rows=self.query("SELECT b.borrow_id,m.member_name,bk.title,b.borrow_date,b.return_date,b.status FROM Borrowing b JOIN Members m ON b.member_id=m.member_id JOIN Books bk ON b.book_id=bk.book_id ORDER BY b.borrow_id DESC LIMIT 10")
            for r in rows: tr.insert('', 'end',values=r)
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
    def tree(self,parent,cols,widths=None):
        tr=ttk.Treeview(parent,columns=cols,show='headings');
        for i,c in enumerate(cols): tr.heading(c,text=c); tr.column(c,width=widths[i] if widths else 130)
        return tr

    def show_books(self):
        self.clear()
        self.title('Books', 'Manage books and available copies')

        top = tk.Frame(self.content, bg='#f4f6f8')
        top.pack(fill='x', padx=25)

        tk.Label(
            top,
            text='Search:',
            bg='#f4f6f8',
            font=('Arial', 10, 'bold')
        ).pack(side='left')

        s = tk.Entry(top, width=30)
        s.pack(side='left', padx=10, ipady=6)

        box = tk.Frame(
            self.content,
            bg='white',
            bd=1,
            relief='solid'
        )
        box.pack(
            fill='both',
            expand=True,
            padx=25,
            pady=15
        )

        tr = self.tree(
            box,
            ('ID', 'Title', 'Author', 'Category', 'Available Copies'),
            [60, 250, 180, 150, 140]
        )
        tr.pack(
            fill='both',
            expand=True,
            padx=10,
            pady=10
        )

        # Search
        tk.Button(
            top,
            text='Search',
            command=lambda: self.load_books(tr, s.get()),
            bg='#172033',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='left', padx=3)

        # Clear
        tk.Button(
            top,
            text='Clear',
            command=lambda: self.clear_book_search(s, tr),
            bg='#555b66',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='left', padx=3)

        # Refresh
        tk.Button(
            top,
            text='Refresh',
            command=lambda: self.load_books(tr),
            bg='#e67e22',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='left', padx=3)

        # Add Book
        tk.Button(
            top,
            text='Add Book',
            command=self.add_book,
            bg='#172033',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='right')

        self.load_books(tr)

    def clear_book_search(self, search_box, tree):
        search_box.delete(0, tk.END)
        self.load_books(tree)
    def load_books(self,tr,s=''):
        for i in tr.get_children(): tr.delete(i)
        try:
            if s.strip(): rows=self.query("SELECT b.book_id,b.title,COALESCE(a.author_name,'Unknown'),b.category,b.available_copies FROM Books b LEFT JOIN Authors a ON b.author_id=a.author_id WHERE b.title LIKE %s OR b.category LIKE %s ORDER BY b.book_id",('%'+s+'%','%'+s+'%'))
            else: rows=self.query("SELECT b.book_id,b.title,COALESCE(a.author_name,'Unknown'),b.category,b.available_copies FROM Books b LEFT JOIN Authors a ON b.author_id=a.author_id ORDER BY b.book_id")
            for r in rows: tr.insert('', 'end',values=r)
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
    def add_book(self):
        w=tk.Toplevel(self.root); w.title('Add Book'); w.geometry('420x430'); w.grab_set(); w.configure(bg='#f4f6f8'); es={}
        for lab in ['Title','Author','Category','Available Copies']:
            tk.Label(w,text=lab,bg='#f4f6f8',font=('Arial',10,'bold')).pack(anchor='w',padx=40,pady=(10,3)); e=tk.Entry(w); e.pack(fill='x',padx=40,ipady=6); es[lab]=e
        def save():
            try: copies=int(es['Available Copies'].get())
            except: messagebox.showerror('Error','Available copies must be a number'); return
            if not all(es[x].get().strip() for x in es): messagebox.showwarning('Required','Fill all fields'); return
            try:
                c=db(); cur=c.cursor(); cur.execute('SELECT author_id FROM Authors WHERE author_name=%s',(es['Author'].get().strip(),)); r=cur.fetchone()
                if r: aid=r[0]
                else: cur.execute('INSERT INTO Authors(author_name) VALUES(%s)',(es['Author'].get().strip(),)); aid=cur.lastrowid
                cur.execute('INSERT INTO Books(title,author_id,category,available_copies) VALUES(%s,%s,%s,%s)',(es['Title'].get().strip(),aid,es['Category'].get().strip(),copies)); c.commit(); cur.close(); c.close(); w.destroy(); self.show_books(); messagebox.showinfo('Success','Book added successfully')
            except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
        tk.Button(w,text='Save Book',command=save,bg='#172033',fg='white',relief='flat',padx=20,pady=10).pack(pady=25)

    def load_members(self, tree, search=''):
        for item in tree.get_children():
            tree.delete(item)

        try:
            conn = db()
            cur = conn.cursor()

            if search.strip():
                cur.execute(
                    """
                    SELECT member_id, member_name, phone
                    FROM Members
                    WHERE member_name LIKE %s
                    OR phone LIKE %s
                    """,
                    ('%' + search + '%', '%' + search + '%')
                )
            else:
                cur.execute(
                    """
                    SELECT member_id, member_name, phone
                    FROM Members
                    """
                )

            rows = cur.fetchall()

            print("MEMBERS FROM DATABASE:", rows)

            for row in rows:
                tree.insert('', 'end', values=row)

            cur.close()
            conn.close()

        except Exception as e:
            print("MEMBER ERROR:", e)
            messagebox.showerror(
                "Member Error",
                str(e)
            )
    def show_members(self):
        self.clear()
        self.title('Members', 'Manage library members')

        # Top bar
        top = tk.Frame(
            self.content,
            bg='#f4f6f8'
        )
        top.pack(
            fill='x',
            padx=25
        )

        tk.Label(
            top,
            text='Search:',
            bg='#f4f6f8',
            font=('Arial', 10, 'bold')
        ).pack(side='left')

        s = tk.Entry(
            top,
            width=30
        )
        s.pack(
            side='left',
            padx=10,
            ipady=6
        )

        # Main table box
        box = tk.Frame(
            self.content,
            bg='white',
            bd=1,
            relief='solid'
        )
        box.pack(
            fill='both',
            expand=True,
            padx=25,
            pady=15
        )

        tr = self.tree(
            box,
            ('ID', 'Member Name', 'Phone'),
            [80, 300, 200]
        )
        tr.pack(
            fill='both',
            expand=True,
            padx=10,
            pady=10
        )

        # Search button
        tk.Button(
            top,
            text='Search',
            command=lambda: self.load_members(tr, s.get()),
            bg='#172033',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='left', padx=3)

        # Clear button
        tk.Button(
            top,
            text='Clear',
            command=lambda: self.clear_member_search(s, tr),
            bg='#555b66',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='left', padx=3)

        # Refresh button
        tk.Button(
            top,
            text='Refresh',
            command=lambda: self.load_members(tr),
            bg='#e67e22',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='left', padx=3)

        # Add Member
        tk.Button(
            top,
            text='Add Member',
            command=self.add_member,
            bg='#172033',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='right', padx=3)

        # Delete Member
        tk.Button(
            top,
            text='Delete Member',
            command=lambda: self.delete_member(tr),
            bg='#b83232',
            fg='white',
            relief='flat',
            padx=18,
            pady=8
        ).pack(side='right', padx=3)

        self.load_members(tr)

    def clear_member_search(self, search_box, tree):
        search_box.delete(0, tk.END)
        self.load_members(tree)

    def delete_member(self, tree):
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                'Select Member',
                'Please select a member to delete.'
            )
            return

        values = tree.item(selected[0], 'values')
        member_id = values[0]

        confirm = messagebox.askyesno(
            'Delete Member',
            'Are you sure you want to delete this member?'
        )

        if not confirm:
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                'DELETE FROM Members WHERE member_id=%s',
                (member_id,)
            )

            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo(
                'Success',
                'Member deleted successfully.'
            )

            self.load_members(tree)

        except mysql.connector.Error as e:
            messagebox.showerror(
                'Error',
                'Cannot delete this member.\n'
                'The member may have borrowing records.'
            )
    def add_member(self):
        w=tk.Toplevel(self.root); w.title('Add Member'); w.geometry('400x320'); w.grab_set(); w.configure(bg='#f4f6f8'); es=[]
        for lab in ['Member Name','Phone']:
            tk.Label(w,text=lab,bg='#f4f6f8',font=('Arial',10,'bold')).pack(anchor='w',padx=40,pady=(15,3)); e=tk.Entry(w); e.pack(fill='x',padx=40,ipady=6); es.append(e)
        def save():
            if not es[0].get().strip(): messagebox.showwarning('Required','Enter member name'); return
            try: c=db(); cur=c.cursor(); cur.execute('INSERT INTO Members(member_name,phone) VALUES(%s,%s)',(es[0].get().strip(),es[1].get().strip())); c.commit(); cur.close(); c.close(); w.destroy(); self.show_members(); messagebox.showinfo('Success','Member added successfully')
            except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
        tk.Button(w,text='Save Member',command=save,bg='black',fg='white',relief='flat',padx=20,pady=10).pack(pady=20)
    def delete_member(self,tr):
        sel=tr.selection();
        if not sel: messagebox.showwarning('Select Member','Select a member first'); return
        mid=tr.item(sel[0],'values')[0]
        if not messagebox.askyesno('Confirm','Delete this member?'): return
        try:
            c=db(); cur=c.cursor(); cur.execute('SELECT COUNT(*) FROM Borrowing WHERE member_id=%s',(mid,));
            if cur.fetchone()[0]>0: messagebox.showerror('Cannot Delete','This member has borrowing records.'); cur.close(); c.close(); return
            cur.execute('DELETE FROM Members WHERE member_id=%s',(mid,)); c.commit(); cur.close(); c.close(); self.show_members()
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
    def show_borrowing(self):
        self.clear(); self.title('Borrow / Return','Issue books and manage returned books'); top=tk.Frame(self.content,bg='#f4f6f8'); top.pack(fill='x',padx=25); tk.Button(top,text='Borrow Book',command=self.borrow_book,bg='#172033',fg='white',relief='flat',padx=18,pady=9).pack(side='left')
        box=tk.Frame(self.content,bg='white',bd=1,relief='solid'); box.pack(fill='both',expand=True,padx=25,pady=15); tr=self.tree(box,('ID','Member','Book','Borrow Date','Return Date','Status'),[60,170,250,120,120,110]); tr.pack(fill='both',expand=True,padx=10,pady=10)
        try:
            rows=self.query('SELECT b.borrow_id,m.member_name,bk.title,b.borrow_date,b.return_date,b.status FROM Borrowing b JOIN Members m ON b.member_id=m.member_id JOIN Books bk ON b.book_id=bk.book_id ORDER BY b.borrow_id DESC')
            for r in rows: tr.insert('', 'end',values=r)
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
        tk.Button(self.content,text='Return Selected Book',command=lambda:self.return_book(tr),bg='black',fg='white',relief='flat',padx=18,pady=9).pack(anchor='e',padx=25,pady=(0,15))
    def borrow_book(self):
        w=tk.Toplevel(self.root); w.title('Borrow Book'); w.geometry('460x390'); w.grab_set(); w.configure(bg='#f4f6f8');
        tk.Label(w,text='Borrow Book',bg='#f4f6f8',font=('Arial',20,'bold')).pack(pady=20); tk.Label(w,text='Member',bg='#f4f6f8',font=('Arial',10,'bold')).pack(anchor='w',padx=40); mc=ttk.Combobox(w,state='readonly'); mc.pack(fill='x',padx=40,pady=(3,15),ipady=4); tk.Label(w,text='Book',bg='#f4f6f8',font=('Arial',10,'bold')).pack(anchor='w',padx=40); bc=ttk.Combobox(w,state='readonly'); bc.pack(fill='x',padx=40,pady=(3,20),ipady=4)
        try: members=self.query('SELECT member_id,member_name FROM Members ORDER BY member_name'); books=self.query('SELECT book_id,title,available_copies FROM Books WHERE available_copies>0 ORDER BY title')
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e)); w.destroy(); return
        mc['values']=[f'{x[0]} - {x[1]}' for x in members]; bc['values']=[f'{x[0]} - {x[1]} (Available: {x[2]})' for x in books]
        def save():
            if not mc.get() or not bc.get(): messagebox.showwarning('Required','Select member and book'); return
            mid=int(mc.get().split(' - ')[0]); bid=int(bc.get().split(' - ')[0])
            try:
                c=db(); cur=c.cursor(); cur.execute('SELECT available_copies FROM Books WHERE book_id=%s',(bid,)); r=cur.fetchone()
                if not r or r[0]<=0: messagebox.showerror('Unavailable','Book is not available'); cur.close(); c.close(); return
                cur.execute("INSERT INTO Borrowing(book_id,member_id,borrow_date,status) VALUES(%s,%s,%s,'Borrowed')",(bid,mid,date.today())); borrow_id=cur.lastrowid; cur.execute('UPDATE Books SET available_copies=available_copies-1 WHERE book_id=%s',(bid,)); cur.execute("INSERT INTO Fine(borrow_id,amount,payment_status) VALUES(%s,0,'No Fine')",(borrow_id,)); c.commit(); cur.close(); c.close(); w.destroy(); self.show_borrowing(); messagebox.showinfo('Success','Book borrowed successfully')
            except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
        tk.Button(w,text='Borrow Book',command=save,bg='#172033',fg='white',relief='flat',padx=20,pady=10).pack()
    def return_book(self,tr):
        sel=tr.selection();
        if not sel: messagebox.showwarning('Select Borrowing','Select a borrowing record'); return
        vals=tr.item(sel[0],'values'); bid=vals[0]
        if vals[5]=='Returned': messagebox.showinfo('Already Returned','This book is already returned'); return
        if not messagebox.askyesno('Confirm','Mark this book as returned?'): return
        try:
            c=db(); cur=c.cursor(); cur.execute('SELECT book_id FROM Borrowing WHERE borrow_id=%s',(bid,)); r=cur.fetchone()
            if not r: cur.close(); c.close(); return
            cur.execute("UPDATE Borrowing SET return_date=%s,status='Returned' WHERE borrow_id=%s",(date.today(),bid)); cur.execute('UPDATE Books SET available_copies=available_copies+1 WHERE book_id=%s',(r[0],)); c.commit(); cur.close(); c.close(); self.show_borrowing(); messagebox.showinfo('Success','Book returned successfully')
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
    def show_fines(self):
        self.clear(); self.title('Fine Management','View and manage fines'); box=tk.Frame(self.content,bg='white',bd=1,relief='solid'); box.pack(fill='both',expand=True,padx=25,pady=15); tr=self.tree(box,('Fine ID','Member','Book','Amount','Payment Status'),[80,200,250,120,150]); tr.pack(fill='both',expand=True,padx=10,pady=10)
        try:
            for r in self.query('SELECT f.fine_id,m.member_name,b.title,f.amount,f.payment_status FROM Fine f JOIN Borrowing br ON f.borrow_id=br.borrow_id JOIN Members m ON br.member_id=m.member_id JOIN Books b ON br.book_id=b.book_id ORDER BY f.fine_id DESC'): tr.insert('', 'end',values=r)
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))
        tk.Button(self.content,text='Mark Selected as Paid',command=lambda:self.pay_fine(tr),bg='black',fg='white',relief='flat',padx=18,pady=9).pack(anchor='e',padx=25,pady=(0,15))
    def pay_fine(self,tr):
        sel=tr.selection();
        if not sel: messagebox.showwarning('Select Fine','Select a fine record'); return
        fid=tr.item(sel[0],'values')[0]; status=tr.item(sel[0],'values')[4]
        if status in ('Paid','No Fine'): messagebox.showinfo('Completed','This fine is already completed'); return
        try:
            c=db(); cur=c.cursor(); cur.execute("UPDATE Fine SET payment_status='Paid' WHERE fine_id=%s",(fid,)); c.commit(); cur.close(); c.close(); self.show_fines()
        except mysql.connector.Error as e: messagebox.showerror('Database Error',str(e))

    def show_analytics(self):
        self.clear()
        self.title('Analytics', 'Visual insights from your library data')

        # Main analytics area
        area = tk.Frame(
            self.content,
            bg='#f4f6f8'
        )
        area.pack(
            fill='both',
            expand=True,
            padx=25,
            pady=15
        )

        area.grid_columnconfigure(0, weight=1, uniform='cards')
        area.grid_columnconfigure(1, weight=1, uniform='cards')
        area.grid_rowconfigure(0, weight=1)

        # ---------------- LEFT CARD ----------------
        b1 = tk.Frame(
            area,
            bg='white',
            bd=0,
            highlightbackground='#dfe3e8',
            highlightthickness=1
        )
        b1.grid(
            row=0,
            column=0,
            sticky='nsew',
            padx=(0, 10)
        )

        # Left heading
        header1 = tk.Frame(
            b1,
            bg='white'
        )
        header1.pack(
            fill='x',
            padx=20,
            pady=(18, 5)
        )

        tk.Label(
            header1,
            text='Borrowing Status',
            bg='white',
            fg='#172033',
            font=('Arial', 13, 'bold')
        ).pack(anchor='w')

        tk.Label(
            header1,
            text='Overview of current borrowing activity',
            bg='white',
            fg='#7b8494',
            font=('Arial', 6)
        ).pack(anchor='w', pady=(4, 0))

        # Chart area
        self.borrowing_chart_frame = tk.Frame(
            b1,
            bg='white'
        )
        self.borrowing_chart_frame.pack(
            fill='both',
            expand=True,
            padx=15,
            pady=(5, 20)
        )

        # ---------------- RIGHT CARD ----------------
        b2 = tk.Frame(
            area,
            bg='white',
            bd=0,
            highlightbackground='#dfe3e8',
            highlightthickness=1
        )
        b2.grid(
            row=0,
            column=1,
            sticky='nsew',
            padx=(10, 0)
        )

        # Right heading
        header2 = tk.Frame(
            b2,
            bg='white'
        )
        header2.pack(
            fill='x',
            padx=20,
            pady=(18, 5)
        )

        tk.Label(
            header2,
            text='Books by Category',
            bg='white',
            fg='#172033',
            font=('Arial', 13, 'bold')
        ).pack(anchor='center')

        tk.Label(
            header2,
            text='Distribution of books across categories',
            bg='white',
            fg='#7b8494',
            font=('Arial', 9)
        ).pack(anchor='center', pady=(4, 0))

        # Chart area
        self.category_chart_frame = tk.Frame(
            b2,
            bg='white'
        )
        self.category_chart_frame.pack(
            fill='both',
            expand=True,
            padx=15,
            pady=(5, 20)
        )

        # Automatically load charts
        self.create_borrowing_chart()
        self.create_category_chart()
    def create_borrowing_chart(self):
        for w in self.borrowing_chart_frame.winfo_children(): w.destroy()
        try: data=self.query('SELECT status,COUNT(*) FROM Borrowing GROUP BY status')
        except mysql.connector.Error as e: tk.Label(self.borrowing_chart_frame,text=str(e),bg='white',fg='red').pack(expand=True); return
        if not data: tk.Label(self.borrowing_chart_frame,text='No borrowing data available',bg='white',fg='#6b7280').pack(expand=True); return
        fig=Figure(figsize=(7,2.8),dpi=90); ax=fig.add_subplot(111); ax.bar([r[0] for r in data],[r[1] for r in data]); ax.set_ylabel('Number of Books'); ax.grid(axis='y',alpha=.25); fig.tight_layout(); canvas=FigureCanvasTkAgg(fig,master=self.borrowing_chart_frame); canvas.draw(); canvas.get_tk_widget().pack(fill='both',expand=True,padx=10,pady=3)
    def create_category_chart(self):
        for w in self.category_chart_frame.winfo_children(): w.destroy()
        try: data=self.query('SELECT category,COUNT(*) FROM Books GROUP BY category ORDER BY COUNT(*) DESC')
        except mysql.connector.Error as e: tk.Label(self.category_chart_frame,text=str(e),bg='white',fg='red').pack(expand=True); return
        if not data: tk.Label(self.category_chart_frame,text='No category data available',bg='white',fg='#6b7280').pack(expand=True); return
        fig=Figure(figsize=(7,2.8),dpi=90); ax=fig.add_subplot(111); ax.pie([r[1] for r in data],labels=[r[0] for r in data],autopct='%1.0f%%',startangle=90); fig.tight_layout(); canvas=FigureCanvasTkAgg(fig,master=self.category_chart_frame); canvas.draw(); canvas.get_tk_widget().pack(fill='both',expand=True,padx=10,pady=3)

def login():
    if username_entry.get().strip()=='admin' and password_entry.get().strip()=='admin123':
        for w in root.winfo_children(): w.destroy()
        root.geometry('1200x700'); root.resizable(True,True); LibraryApp(root)
    else: messagebox.showerror('Login Failed','Invalid username or password')

root=tk.Tk(); root.title('NEXORA - Smart Library Platform'); root.geometry('500x420'); root.resizable(False,False); root.configure(bg='#172033')
card=tk.Frame(root,bg='white'); card.pack(fill='both',expand=True,padx=55,pady=45)
tk.Label(card,text='NEXORA',bg='white',fg='#172033',font=('Arial',26,'bold')).pack(pady=(35,3)); tk.Label(card,text='SMART LIBRARY PLATFORM',bg='white',fg='#6b7280',font=('Arial',9,'bold')).pack(pady=(0,25))
tk.Label(card,text='Username',bg='white',font=('Arial',10,'bold')).pack(anchor='w',padx=45); username_entry=tk.Entry(card); username_entry.pack(fill='x',padx=45,pady=(4,15),ipady=7)
tk.Label(card,text='Password',bg='white',font=('Arial',10,'bold')).pack(anchor='w',padx=45); password_entry=tk.Entry(card,show='*'); password_entry.pack(fill='x',padx=45,pady=(4,20),ipady=7)
tk.Button(card,text='LOGIN',command=login,bg='#172033',fg='white',relief='flat',font=('Arial',11,'bold'),padx=30,pady=10).pack(); tk.Label(card,text='Demo Login: admin / admin123',bg='white',fg='#9ca3af',font=('Arial',8)).pack(pady=15)
root.bind('<Return>',lambda e:login()); root.mainloop()
