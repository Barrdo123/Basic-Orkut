import os
from platform import system
from flask import *
from models import db
from models import Usuario, Post
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

sucesso_cadastro = False
if system() == "Windows":
    sqlite_prefixo = "sqlite:///"
else:
    sqlite_prefixo = "sqlite:////"

pasta_atual = os.path.abspath(os.path.dirname(__file__))
uri_db = sqlite_prefixo + pasta_atual + '/database/banco.sqlite'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sgrdo'
app.config['SQLALCHEMY_DATABASE_URI'] = uri_db
db.init_app(app)

def login_required(funcao):
    @wraps(funcao)
    def inner(*args, **kwargs):
        if 'logado' in session:
            return funcao(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return inner




@app.route("/")
def index():
    if not 'logado' in session:
        return render_template("auth/index.html")
    return redirect(url_for('posts'))



@app.route('/postar', methods=['GET', 'POST'])
@login_required
def postar():
    if request.method == 'POST':
        new_post = Post(
            conteudo=request.form['post'],
            para=session['logado']['usuario'],
            de=session['logado']['usuario']
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('posts'))
    else:
        return render_template('profile/postar.html')



@app.route('/posts')
@login_required
def posts():
    user = session['logado']

    posts = Post.query.filter_by(
        de=user['usuario'],  
        para=user['usuario'] 
    ).order_by(
        Post.criado_em.desc(), 
    ).all() 

    return render_template('profile/posts.html', user=user, posts=posts)



@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if 'logado' in session:
            return redirect(url_for('index'))
        sucesso = False
        if 'sucesso_cadastro' in session:
            sucesso = session['sucesso_cadastro']
        session['sucesso_cadastro'] = False
        return render_template("auth/login.html", sucesso_cadastro=sucesso)
    else:
        user = Usuario.query.filter_by(usuario=request.form['usuario']).first()
        if user == None:
            return "usuario nao cadastrado"
        else:
            if check_password_hash(user.senha, request.form['senha']):
                session['logado'] = {
                    "nome": user.nome,
                    "usuario": user.usuario,
                    "sobrenome": user.sobrenome
                }
                return redirect(url_for('index'))
            else:
                return "senha incorreta"


@app.route('/cadastrar', methods=["POST", "GET"])
def cadastrar():
    if request.method == "GET":
        session['sucesso_cadastro'] = False
        return render_template("auth/cadastrar.html")
    else:
        dados = request.form
        senha_hash = generate_password_hash(dados['senha'])
        user = Usuario(
            usuario=dados['usuario'],
            nome=dados['nome'],
            sobrenome=dados['sobrenome'],
            senha=senha_hash
        )
        db.session.add(user)
        db.session.commit()
        session['sucesso_cadastro'] = True
        return redirect(url_for("login"))


@app.route("/listar/usuarios")
@login_required
def listar_usuarios():
    users = Usuario.query.all()

    return render_template(
        "usuarios.html",
        usuarios=users
    )

@app.route("/logout")
@login_required
def logout():
    del session['logado']

    return redirect(url_for('login'))



@app.route("/post/<id>", methods=['GET', 'DELETE'])
@login_required

def post(id):
    user = session['logado']
    query = Post.query.filter_by(id=id)


    if request.method == 'GET':
        post = query.first()
        if post:
            return f"<h3>De: {post.de}</h3><h3>Para: {post.para}</h3><pre>{post.conteudo}</pre>"
        else:
            return 'post nao encontrado'

    else:
        deletions = query.where((Post.para==user['usuario']) | (Post.de==user['usuario'])).delete()
        db.session.commit()
        return jsonify({"deletions": deletions})

@app.route("/existe/<user>")
def existe(user):
    user = Usuario.query.filter_by(usuario=user).first()
    return jsonify({"existe": bool(user)})



@app.route('/<username>/posts')
@login_required
def usuario(username):

    user = Usuario.query.filter_by(usuario=username).first()

    if user == None:
        return 'Usuario não existe'
    
    posts = Post.query.filter_by(de=username, para=username).order_by(
        Post.criado_em.desc(),
    ).all()

    return render_template(
        'usuario/posts.html',
        nome=user.nome,
        sobrenome=user.sobrenome,
        usuario=user.usuario,
        posts=posts
    )

@app.route('/depoimentos')
def depoimentos():
    user = session['logado']
    posts= Post.query.where(Post.de!= user['usuario']).filter_by(para=user['usuario']).all()
    return render_template('/profile/depoimentos.html', posts=posts,
                           nome=user['usuario'])



@app.route('/<username>/postar', methods=['GET', 'POST'])
@login_required
def postar_depoimento(username):
    para = Usuario.query.filter_by(usuario=username).first()

    if para == None:
        return 'Usuario não existe'
    else:
        if request.method == 'GET':
            return render_template('usuario/postar.html', nome=para.nome, usuario=para.usuario)
        else:
            new_post = Post(
                conteudo=request.form['post'],
                para=username,
                de=session['logado']['usuario']
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(f"/{username}/depoimentos")

@app.route('/<username>/depoimentos')
@login_required
def usuario_depoimentos(username):
    user = Usuario.query.filter_by(usuario=username).first() 
    if user == None:
        return 'Usuario não existe'

    posts = Post.query.where(Post.de!= username).filter_by(para=username
    ).order_by(
        Post.criado_em.desc(),
    ).all()

    print(posts)

    return render_template('/usuario/depoimentos.html', usuario=username,posts=posts)



with app.app_context():
    db.create_all()

app.run(debug=True)
