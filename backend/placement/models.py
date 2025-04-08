from django.db import models

# Create your models here.
class Container(models.Model):
    name = models.CharField(max_length=100)
    width_cm = models.FloatField()
    height_cm = models.FloatField()
    depth_cm = models.FloatField()
    max_weight_kg = models.FloatField()
    zone = models.CharField(max_length=50)
    used_volume = models.FloatField(default=0)
    used_weight = models.FloatField(default=0)
    is_full = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.zone})"

    @property
    def total_volume(self):
        return self.width_cm * self.height_cm * self.depth_cm
    
    @property
    def utilization_percentage(self):
        if self.total_volume == 0:
            return 0
        return (self.used_volume / self.total_volume) * 100

class Item(models.Model):
    name = models.CharField(max_length=100)
    width_cm = models.FloatField()
    height_cm = models.FloatField()
    depth_cm = models.FloatField()
    weight_kg = models.FloatField()
    priority = models.IntegerField(default=1)
    preferred_zone = models.CharField(max_length=50, blank=True, null=True)
    is_placed = models.BooleanField(default=False)
    container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
    position_x = models.FloatField(null=True, blank=True)
    position_y = models.FloatField(null=True, blank=True)
    position_z = models.FloatField(null=True, blank=True)
    rotation = models.IntegerField(null=True, blank=True)
    placement_date = models.DateTimeField(null=True, blank=True)
    sensitive = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} (Priority: {self.priority})"
    
    @property
    def volume(self):
        return self.width_cm * self.height_cm * self.depth_cm

class PlacementHistory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    placement_date = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    reason = models.TextField(blank=True)
    
    def __str__(self):
        status = "Successful" if self.success else "Failed"
        return f"{status} placement of {self.item.name} in {self.container.name} on {self.placement_date}"
