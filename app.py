# =============================================================================
# LOKALOOK - FLASK WEB APPLICATION
# =============================================================================

# --- 1. Import Library ---
import os
import urllib.parse
from markupsafe import Markup, escape

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate  # type: ignore

# --- 2. Konfigurasi Aplikasi Flask ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'inirahasialho-gantikalauproduction')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lokalook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. Inisialisasi Ekstensi ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Anda harus login untuk mengakses halaman ini."
login_manager.login_message_category = "warning"

# --- 4. Model Database ---
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'  # For easier debugging

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Integer, default=0)  # kolom stok produk

    def __repr__(self):
        return f'<Product {self.name}>'  # For easier debugging

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# --- 5. Rute untuk Pengguna Umum (Frontend) ---
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s is None:
        return ''
    escaped = escape(s)
    return Markup(escaped.replace('\n', '<br>\n'))  # Consistent with HTML line breaks

@app.route('/')
def index():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def detail_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('detail_product.html', product=product)

@app.route('/cart')
def cart():
    cart_products = []
    total_price = 0

    if 'cart' in session:
        for product_id_str, details in session['cart'].items():
            product_id = int(product_id_str)
            product = Product.query.get(product_id)  # Fetch from DB

            if product:  # Ensure product exists
                qty = details.get('qty', 0)
                subtotal = product.price * qty

                cart_products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'qty': qty,
                    'subtotal': subtotal
                })
                total_price += subtotal

    return render_template('cart.html', cart_products=cart_products, total_price=total_price)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)  # Ensure product exists

    if 'cart' not in session:
        session['cart'] = {}

    product_id_str = str(product_id)

    if product_id_str not in session['cart']:
        session['cart'][product_id_str] = {'qty': 1}
    else:
        session['cart'][product_id_str]['qty'] += 1

    session.modified = True  # Penting agar Flask menyimpan perubahan session
    flash('Produk berhasil ditambahkan ke keranjang!', 'success')
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified = True
        flash('Produk berhasil dihapus dari keranjang!', 'success')
        return '', 200  # Consistent return
    return '', 404  # Consistent return

@app.route('/checkout')
def checkout():
    cart = session.get('cart', {})  # Get cart from session, default to empty dict
    if not cart:
        flash('Keranjang Anda kosong, tidak bisa checkout.', 'warning')
        return redirect(url_for('cart'))  # Redirect to cart, not view_cart (which doesn't exist)

    product_counts = {}
    for product_id_str in cart:
        product_counts[int(product_id_str)] = cart[product_id_str].get('qty', 0)

    products = Product.query.filter(Product.id.in_(product_counts.keys())).all()
    total_price = 0
    message = "Halo Admin Lokalook, saya ingin memesan produk berikut:\n\n"

    for product in products:
        qty = product_counts[product.id]
        subtotal = product.price * qty
        total_price += subtotal
        message += f"- {product.name} x{qty} (Rp {subtotal:,})\n"

    message += f"\n*Total Pesanan: Rp {total_price:,}*\n\nTerima kasih!"

    whatsapp_number = "6288286833950"
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={whatsapp_number}&text={encoded_message}"
    session.pop('cart', None)
    return redirect(whatsapp_url)

# --- 6. Rute untuk Admin ---
@app.route('/admin')
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template('admin_dashboard.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if Admin.query.first():
        flash('Registrasi admin sudah ditutup.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_admin = Admin(username=username)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        flash('Registrasi Admin berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    next_page = request.args.get('next')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            # Send a flag to the next page to trigger animation
            return redirect(next_page or url_for('admin_dashboard', show_animation=True))
        else:
            flash('Login gagal. Periksa kembali username dan password Anda.', 'danger')

    return render_template('login.html', next_page=next_page, admin_exists=Admin.query.first() is not None) # Pass admin_exists
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        try:
            price = int(request.form['price'])
        except ValueError:
            flash('Harga harus berupa angka.', 'danger')
            return redirect(url_for('add_product'))

        description = request.form['description']
        image_url = request.form['image_url']
        stock = int(request.form.get('stock', 0))  # Get stock, default to 0
        new_product = Product(name=name, price=price, description=description, image_url=image_url, stock=stock)
        db.session.add(new_product)
        db.session.commit()
        flash('Produk baru berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_product.html')

@app.route('/delete_item/<int:id>', methods=['POST'])
def delete_item(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produk berhasil dihapus.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/product/<int:id>/update_stock', methods=['POST'])
@login_required
def update_stock(id):
    product = Product.query.get_or_404(id)
    new_stock = request.form.get('stock')
    try:
        new_stock = int(new_stock)
        if new_stock < 0:
            flash('Stok tidak boleh negatif', 'danger')
        else:
            product.stock = new_stock
            db.session.commit()
            flash(f'Stok produk "{product.name}" berhasil diperbarui.', 'success')
    except ValueError:
        flash('Input stok harus berupa angka.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        try:
            product.name = request.form['name']
            product.price = int(request.form['price'])
            product.stock = int(request.form['stock'])
            product.description = request.form.get('description')
            product.image_url = request.form['image_url']

            if product.price < 0 or product.stock < 0:
                flash('Harga dan stok tidak boleh negatif.', 'danger')
                return redirect(url_for('edit_product', id=id))

            db.session.commit()
            flash(f'Produk "{product.name}" berhasil diperbarui.', 'success')
            return redirect(url_for('admin_dashboard'))
        except ValueError:
            flash('Harga dan stok harus berupa angka valid.', 'danger')
        except Exception as e:
            flash(f'Terjadi kesalahan saat memperbarui produk: {e}', 'danger')  # Log the exception

    return render_template('edit_product.html', product=product)

# --- 7. Rute untuk Halaman Statis ---
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    filtered_products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    return render_template('index.html', products=filtered_products)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)