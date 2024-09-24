from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_GET
import datetime
from .models import SnapshotList
import base64
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
def get_home(request): 
    return render(request, 'home.htm') 

def dangKi(request): 
    form = CreateUserForm()
    context = {'form':form}
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
    return render(request, 'register.htm', context) 

def dangNhap(request): 
    #if request.user.is_authenticated:
     #   return redirect('login')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Kiểm tra lại tên tài khoản hoặc mật khẩu')
    context = {}
    return render(request, 'login.htm', context) 

def logoutPage(request):
    logout(request)
    return redirect('login')

@login_required
@require_GET
def get_timeline_data(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Thiếu tham số ngày.'}, status=400)
    
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Định dạng ngày không hợp lệ. Vui lòng sử dụng YYYY-MM-DD.'}, status=400)
    
    # Truy xuất dữ liệu từ cơ sở dữ liệu MySQL
    snapshots = SnapshotList.objects.filter(date=selected_date).order_by('time')
    
    if not snapshots.exists():
        return JsonResponse({'events': []})
    
    timeline_data = {}
    
    # Chuyển đổi dữ liệu truy xuất được thành định dạng mong muốn
    for snapshot in snapshots:
        event_time = snapshot.time.strftime('%H:%M:%S')
        event_date_str = snapshot.date.strftime('%Y-%m-%d')
        
        event = {
            "time": event_time,
            "event": snapshot.event,
            "image_url": snapshot.image_url,  # có thể cần xử lý URL ảnh nếu cần
            "camera": snapshot.camera, 
            "date" : event_date_str,
        }
        
        if event_date_str not in timeline_data:
            timeline_data[event_date_str] = []
        
        timeline_data[event_date_str].append(event)
    
    data = timeline_data.get(date_str, [])
    return JsonResponse({'events': data})

@login_required
@csrf_protect
def upload_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            event = data.get('event', 'Chụp hình')  # Lấy thông tin sự kiện từ frontend hoặc đặt mặc định
            camera = data.get('camera', 1)  # Lấy thông tin camera từ frontend hoặc đặt mặc định

            if not image_data:
                return JsonResponse({'success': False, 'error': 'Không có dữ liệu hình ảnh'}, status=400)

            # Xử lý dữ liệu base64
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]  # Lấy đuôi file (ví dụ: png)

            # Tạo tên file duy nhất
            now = datetime.datetime.now()
            timestamp = now.strftime("%H_%M_%S_%d_%m_%Y")
            file_name = f"snapshot_{timestamp}.{ext}"

            # Đường dẫn lưu trữ
            file_path = os.path.join(settings.MEDIA_ROOT, 'app', 'images', file_name)
            # file_path = os.path.join(settings.STATIC_URL, 'app', 'images', file_name)

            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Giải mã base64 và lưu file
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(imgstr))

            # chỉ lưu tên file
            image_url = file_name

            # Tạo bản ghi mới trong SnapshotList
            snapshot = SnapshotList.objects.create(
                time=now.time(),
                event=event,
                image_url=image_url,  # Lưu đường dẫn đến hình ảnh
                end_time=now.time(),  # Vì là hình ảnh nên time = end_time
                camera=camera,
                date=now.date()
            )

            return JsonResponse({
                'success': True,
                'file_name': file_name,
                'image_url': image_url,
                'snapshot_id': snapshot.id
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Phương thức không được hỗ trợ'}, status=405)

@login_required
@require_GET
def show_snapshot(request):
    url_str = request.GET.get('url')
    
    if not url_str:
        raise Http404("URL không tồn tại")

    # Đường dẫn tới file
    file_path = os.path.join(settings.MEDIA_ROOT, 'app', 'images', url_str)

    # Kiểm tra file có tồn tại không
    if not os.path.exists(file_path):
        raise Http404("File không tồn tại")
    
    # Trả về ảnh dưới dạng FileResponse
    return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
    
