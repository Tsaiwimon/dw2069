"""
Views for Sales Frontend System.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q
from apps.ecommerce.models import Product, Category, Cart, CartItem
from django.contrib.auth.mixins import LoginRequiredMixin


class SalesHomeView(TemplateView):
    """Home page for sales frontend."""
    template_name = 'sales/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_active=True)[:6]
        context['categories'] = Category.objects.filter(is_active=True)[:6]
        return context


class SalesProductsView(ListView):
    """Products listing page."""
    template_name = 'sales/products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Sorting
        sort = self.request.GET.get('sort', '')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class SalesProductDetailView(DetailView):
    """Product detail page."""
    model = Product
    template_name = 'sales/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:6]
        return context


class SalesCartView(TemplateView):
    """Shopping cart page."""
    template_name = 'sales/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.request.user)
                context['cart'] = cart
                context['cart_items'] = cart.items.all()
                context['cart_total'] = cart.total_price
            except Cart.DoesNotExist:
                context['cart'] = None
                context['cart_items'] = []
                context['cart_total'] = 0
        else:
            context['cart'] = None
            context['cart_items'] = []
            context['cart_total'] = 0
        
        return context


class SalesCheckoutView(LoginRequiredMixin, TemplateView):
    """Checkout page."""
    template_name = 'sales/checkout.html'
    login_url = 'admin:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            cart = Cart.objects.get(user=self.request.user)
            context['cart'] = cart
            context['cart_items'] = cart.items.all()
            context['subtotal'] = cart.total_price
        except Cart.DoesNotExist:
            context['cart'] = None
            context['cart_items'] = []
            context['subtotal'] = 0
        
        return context


class SalesOrderHistoryView(LoginRequiredMixin, TemplateView):
    """Order history page."""
    template_name = 'sales/order_history.html'
    login_url = 'admin:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.ecommerce.models import Order
        context['orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        return context
