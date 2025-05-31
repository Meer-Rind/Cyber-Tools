import socket
from urllib.parse import urlparse
from django.conf import settings
import requests
import hashlib
import re
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EducationBlog, PhishingScanResult
from .forms import (
    EducationBlogForm,
    PhishingScanForm,
    PortScanForm, 
    PasswordStrengthForm, 
    HashGeneratorForm,
    URLScanForm
)
from .models import ScanResult, PasswordAudit

from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView
from django.urls import reverse, reverse_lazy

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'securitytools/register.html'
    
    def get_success_url(self):
        return reverse('dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            # Return form with errors
            return render(request, 'securitytools/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'securitytools/login.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'securitytools/dashboard.html')
    else:
        return redirect('login')


@login_required
def port_scan(request):
    # Common port to service mapping
    PORT_SERVICE_MAP = {
        20: 'FTP (Data)',
        21: 'FTP (Control)',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        3306: 'MySQL',
        3389: 'RDP',
        # Add more ports as needed
    }

    if request.method == 'POST':
        form = PortScanForm(request.POST)
        if form.is_valid():
            target = form.cleaned_data['target']
            scan_type = form.cleaned_data['scan_type']
            ports = form.cleaned_data['ports']
            
            try:
                # Simple port scanning logic
                open_ports = []
                port_results = []
                
                if scan_type == 'quick':
                    port_range = range(1, 101)  # Top 100 ports
                elif scan_type == 'full':
                    port_range = range(1, 65536)
                else:
                    port_range = map(int, ports.split(','))
                
                for port in port_range:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((target, port))
                    if result == 0:
                        open_ports.append(str(port))
                        port_results.append({
                            'port': port,
                            'service': PORT_SERVICE_MAP.get(port, 'Unknown')
                        })
                    sock.close()
                
                result_text = f"Open ports on {target}: {', '.join(open_ports)}"
                
                # Save scan result
                ScanResult.objects.create(
                    user=request.user,
                    scan_type=f"Port Scan ({scan_type})",
                    target=target,
                    result=result_text
                )
                
                messages.success(request, 'Scan completed successfully!')
                return render(request, 'securitytools/port_scan.html', {
                    'form': form,
                    'result': result_text,
                    'port_results': port_results,
                    'target': target
                })
                
            except Exception as e:
                messages.error(request, f'Error during scan: {str(e)}')
    else:
        form = PortScanForm()
    
    return render(request, 'securitytools/port_scan.html', {
        'form': form,
        'port_results': None
    })

@login_required
def password_strength(request):
    if request.method == 'POST':
        form = PasswordStrengthForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            strength = "Weak"
            score = 0
            
            # Length check
            if len(password) >= 8:
                score += 1
            if len(password) >= 12:
                score += 1
            
            # Complexity checks
            if re.search(r'[A-Z]', password):
                score += 1
            if re.search(r'[a-z]', password):
                score += 1
            if re.search(r'[0-9]', password):
                score += 1
            if re.search(r'[^A-Za-z0-9]', password):
                score += 1
            
            if score <= 2:
                strength = "Very Weak"
            elif score <= 4:
                strength = "Weak"
            elif score <= 6:
                strength = "Moderate"
            else:
                strength = "Strong"
            
            # Save audit
            PasswordAudit.objects.create(
                user=request.user,
                password=password[:2] + '*'*(len(password)-2),  # Don't store full password
                strength=strength
            )
            
            messages.success(request, f'Password strength: {strength}')
            return render(request, 'securitytools/password_strength.html', {
                'form': form,
                'strength': strength,
                'score': score,
                'max_score': 7
            })
    else:
        form = PasswordStrengthForm()
    
    return render(request, 'securitytools/password_strength.html', {'form': form})

@login_required
def hash_generator(request):
    if request.method == 'POST':
        form = HashGeneratorForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            algorithm = form.cleaned_data['algorithm']
            
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(text.encode('utf-8'))
            hash_result = hash_obj.hexdigest()
            
            return render(request, 'securitytools/hash_generator.html', {
                'form': form,
                'hash_result': hash_result,
                'algorithm': algorithm.upper()
            })
    else:
        form = HashGeneratorForm()
    
    return render(request, 'securitytools/hash_generator.html', {'form': form})

@login_required
def url_scanner(request):
    if request.method == 'POST':
        form = URLScanForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            try:
                # Check if URL exists
                response = requests.get(url, timeout=10)
                status = f"URL is reachable (Status: {response.status_code})"
                
                # Check for common vulnerabilities
                vulnerabilities = []
                if 'sql' in response.text.lower():
                    vulnerabilities.append("Potential SQL injection vulnerability")
                if '<script>' in response.text.lower():
                    vulnerabilities.append("Potential XSS vulnerability")
                
                result = {
                    'status': status,
                    'vulnerabilities': vulnerabilities if vulnerabilities else ["No obvious vulnerabilities detected"],
                    'headers': dict(response.headers)
                }
                
                # Save scan result
                ScanResult.objects.create(
                    user=request.user,
                    scan_type="URL Scan",
                    target=url,
                    result=str(result)
                )
                
                return render(request, 'securitytools/url_scanner.html', {
                    'form': form,
                    'result': result
                })
                
            except requests.RequestException as e:
                messages.error(request, f'Error scanning URL: {str(e)}')
    else:
        form = URLScanForm()
    
    return render(request, 'securitytools/url_scanner.html', {'form': form})

@login_required
def scan_history(request):
    scans = ScanResult.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'securitytools/scan_history.html', {'scans': scans})




def education_home(request):
    featured_blogs = EducationBlog.objects.filter(is_featured=True).order_by('-published_date')[:3]
    recent_blogs = EducationBlog.objects.all().order_by('-published_date')[:5]
    return render(request, 'securitytools/education_home.html', {
        'featured_blogs': featured_blogs,
        'recent_blogs': recent_blogs
    })

def blog_detail(request, slug):
    blog = get_object_or_404(EducationBlog, slug=slug)
    related_blogs = EducationBlog.objects.exclude(id=blog.id).order_by('-published_date')[:3]
    return render(request, 'securitytools/blog_detail.html', {
        'blog': blog,
        'related_blogs': related_blogs
    })

@login_required
def create_blog(request):
    if request.method == 'POST':
        form = EducationBlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save()
            messages.success(request, 'Blog created successfully!')
            return redirect('blog_detail', slug=blog.slug)
    else:
        form = EducationBlogForm()
    return render(request, 'securitytools/create_blog.html', {'form': form})



@login_required
def phishing_detector(request):
    if request.method == 'POST':
        form = PhishingScanForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Basic checks (you can enhance this with APIs like Google Safe Browsing)
            domain = urlparse(url).netloc.lower()
            
            # Common phishing indicators
            suspicious_keywords = ['login', 'account', 'verify', 'secure', 'banking', 'paypal']
            is_phishing = any(keyword in domain for keyword in suspicious_keywords)
            
            # Check for IP addresses in domain (common in phishing)
            is_ip = any(part.isdigit() for part in domain.split('.'))
            
            # Check for URL shortening services
            url_shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 'is.gd']
            is_shortened = any(shortener in domain for shortener in url_shorteners)
            
            # Check domain age (you would need an API for this in production)
            domain_age = "N/A"
            
            # Check SSL certificate (you would need an API for this in production)
            has_ssl = url.startswith('https://')
            
            # Save results
            result = PhishingScanResult.objects.create(
                user=request.user if request.user.is_authenticated else None,
                url=url,
                is_phishing=is_phishing or is_ip or is_shortened,
                details={
                    'domain': domain,
                    'has_ssl': has_ssl,
                    'is_ip_address': is_ip,
                    'is_shortened_url': is_shortened,
                    'suspicious_keywords_found': suspicious_keywords,
                }
            )
            
            return render(request, 'securitytools/phishing_result.html', {
                'form': form,
                'result': result,
                'domain': domain,
                'is_ip': is_ip,
                'is_shortened': is_shortened,
                'has_ssl': has_ssl,
                'domain_age': domain_age,
            })
    else:
        form = PhishingScanForm()
    
    return render(request, 'securitytools/phishing_detector.html', {'form': form})