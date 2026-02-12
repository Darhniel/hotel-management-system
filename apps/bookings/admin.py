# bookings/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Booking, BookingLog

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = [
        'customer_name', 
        'hotel', 
        'room', 
        'check_in', 
        'check_out',
        'status',
        'created_by',
        'created_at',
        'get_total_nights'
    ]
    
    # Add filters on the right sidebar
    list_filter = [
        'status',
        'hotel',
        'check_in',
        'check_out',
        'created_at'
    ]
    
    # Add search functionality
    search_fields = [
        'customer_name',
        'customer_email',
        'room__room_number',
        'hotel__name'
    ]
    
    # Date-based navigation
    date_hierarchy = 'check_in'
    
    # Pagination
    list_per_page = 25
    
    # Ordering
    ordering = ['-created_at']
    
    # Fields to display in detail view
    fieldsets = [
        ('Booking Information', {
            'fields': [
                'hotel',
                'room',
                'customer_name',
                'customer_email',
                ('check_in', 'check_out')
            ]
        }),
        ('Status & Payment', {
            'fields': [
                'status',
                'created_by',
                'cancelled_at'
            ]
        }),
        ('Dates', {
            'fields': [
                'created_at',
            ],
            'classes': ['collapse']  # Collapsible section
        })
    ]
    
    # Read-only fields
    readonly_fields = ['created_at']
    
    # Actions in the admin
    actions = ['mark_as_checked_in', 'mark_as_checked_out']
    
    def get_total_nights(self, obj):
        """Calculate total nights stay"""
        if obj.check_out and obj.check_in:
            delta = obj.check_out - obj.check_in
            return delta.days
        return 0
    get_total_nights.short_description = 'Total Nights' # type: ignore
    
    def mark_as_checked_in(self, request, queryset):
        """Admin action to mark bookings as checked in"""
        updated = queryset.update(status='CHECKED_IN')
        self.message_user(request, f'{updated} bookings marked as checked in.')
    mark_as_checked_in.short_description = "Mark selected as Checked In" # type: ignore
    
    def mark_as_checked_out(self, request, queryset):
        """Admin action to mark bookings as checked out"""
        updated = queryset.update(status='CHECKED_OUT')
        self.message_user(request, f'{updated} bookings marked as checked out.')
    mark_as_checked_out.short_description = "Mark selected as Checked Out"
    
    def get_queryset(self, request):
        """Optimize database queries"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'hotel',
            'room',
            'created_by'
        )
        return queryset

@admin.register(BookingLog)
class BookingLogAdmin(admin.ModelAdmin):
    list_display = [
        'booking',
        'action',
        'performed_by',
        'performed_at',
        'get_customer_name'
    ]
    
    list_filter = ['action', 'performed_at']
    search_fields = [
        'booking__customer_name',
        'booking__customer_email',
        'performed_by__username'
    ]
    
    date_hierarchy = 'performed_at'
    
    readonly_fields = ['performed_at']
    
    def get_customer_name(self, obj):
        """Display customer name from booking"""
        return obj.booking.customer_name
    get_customer_name.short_description = 'Customer'
    get_customer_name.admin_order_field = 'booking__customer_name'