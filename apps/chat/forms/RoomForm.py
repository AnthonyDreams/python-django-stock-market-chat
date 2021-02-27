from django import forms
from ..models.ChatRoom import ChatRoom



class RoomCreateForm(forms.ModelForm):
	class Meta:
		model = ChatRoom
		fields = ['name']
		
	def clean(self):
		super().clean()
		
		try:
			name = self.cleaned_data.get('name')
			room = ChatRoom.objects.get(name=name)
			
			raise forms.ValidationError(
				'Room {} already exists'.format(name),
				code='NOT_UNIQUE_ROOM'
			)
			
		except ChatRoom.DoesNotExist:
			return self.cleaned_data