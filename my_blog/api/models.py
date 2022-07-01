from tastypie.resources import ModelResource
from blog.models import Post

# Create your models here.
class BlogpostResource(ModelResource):
    class Meta:
        #lazy loading
        queryset = Post.objects.all()
        resource_name = 'posts'

