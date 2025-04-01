from django.contrib import admin
from django import forms
from dal import autocomplete
from .models import *
# Register your models here.

class Product_images(admin.TabularInline):
    model = Product_image
    
class Additional_infos(admin.TabularInline):
    model = Additional_info
    
class ReviewTubulerinline(admin.TabularInline):
    model = Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'subcategory': autocomplete.ModelSelect2(url='subcategory-autocomplete')
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "Categories" in self.data:  # If a category is selected
            try:
                category_id = int(self.data.get("Categories"))
                self.fields["subcategory"].queryset = Sub_category.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                self.fields["subcategory"].queryset = Sub_category.objects.none()
        elif self.instance.pk:  # If editing an existing product
            self.fields["subcategory"].queryset = self.instance.Categories.sub_category_set.all()
        
class Product_Admin(admin.ModelAdmin):
    inlines = [Product_images, Additional_infos, ReviewTubulerinline]
    list_display = ("product_name","price", "Categories","color", "section")
    list_editable = ("Categories", "section","color")


    
    
class Order_itemTublerinline(admin.TabularInline):
    model = Order_item
    
class OrderAdmin(admin.ModelAdmin):
    inlines = [Order_itemTublerinline]
    list_display = ['firstname','phone','email', 'payment_id', 'paid', 'date']
    search_fields = ['firstname','email', 'payment_id']
    
admin.site.register(Slider)

admin.site.register(Banner_area)

admin.site.register(Main_category)

admin.site.register(Category)

admin.site.register(Sub_category)

admin.site.register(Section)

admin.site.register(Product,Product_Admin)

admin.site.register(Product_image)

admin.site.register(Additional_info)

admin.site.register(Color)

admin.site.register(Brand)

admin.site.register(Coupon_code)

admin.site.register(Order, OrderAdmin)

admin.site.register(Order_item)

admin.site.register(Contact_us)

admin.site.register(Wishlist)

admin.site.register(Review)