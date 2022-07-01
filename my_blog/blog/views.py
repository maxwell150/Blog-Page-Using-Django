from pyexpat.errors import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as user_login
from django.contrib.auth import logout as user_logout
from django.contrib import messages
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPosts, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count

app_name = 'blog'

# Create your views here.
def landing(request):
    """rendering the homepage of my blog"""
    return render(request, 'blog/landing.html')


def login(request):
    """loading the login page"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            user_login(request, user)
            return redirect('blog:homepage')
        else:
            messages.info(request, 'Invalid username or password')
            return redirect('blog:login')
    else:
        return render(request, 'blog/login.html')

def logout(request):
    """Login user out of the system"""
    user_logout(request)
    return redirect('blog:homepage')


def signup(request):
    """function for serving signup/signin as well as authentication of password"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['repeat_password']

        if password == password2:
            if User.objects.filter(email=email).exists():
                """check whether email is already used"""
                messages.info(request, 'Email Already Exists')
                return redirect('blog:signup')
            elif User.objects.filter(username=username).exists():
                """check whether username is already used"""
                messages.info(request, 'Username Already Used')
                return redirect('blog:signup')
            else:
                """if details provided are unique create and save user to database"""
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save();
                return redirect('blog:login')
        else:
            messages.info(request, 'Password does not match')
            return redirect('blog:signup')

    else:
        return render(request, 'blog/signup.html')


def home(request, tag_slug=None):
    """Function for serving the list of posts from database to homepage"""
    post_objects = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_objects = post_objects.filter(tags__in=[tag])
    #adding pagination to my blog page and setting a max of 3 post per page
    paginator = Paginator(post_objects, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/home.html', {'posts': posts,'page': page, 'tag': tag})

def post_info(request, post):
    """function for serving the entire post"""
    post = get_object_or_404(Post,
                                slug=post, status='published')
    #active comments
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Creating a comment obj
            new_comment = comment_form.save(commit=False)
            # Assign current post to comment
            new_comment.post = post
            #save comment to db
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request, 'blog/post.html', {'post': post, 'similar_posts': similar_posts,
                    'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})


def share(request, post_id):
    #currntly not working
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPosts(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"""{data['name']} recommends you read
                        {post.title}"""
            message = f"Read {post.title} at {post_url}\n\n" \
                        f"{data['name']}\'s comments: {data['comments']}"
            send_mail(subject, message, 'email@gmail.com',[data['to']])
            sent = True
    else:
        form = EmailPosts()
    return render(request, 'blog/share.html', {'form': form, 'post': post, 'sent': sent})
