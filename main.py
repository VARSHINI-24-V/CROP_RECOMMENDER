from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini
genai.configure(api_key=GEMINI_KEY)

# Flask app
app = Flask(__name__, template_folder="src")
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# Language mappings for states
STATE_LANGUAGE_MAP = {
    'Tamil Nadu': 'tamil',
    'Karnataka': 'kannada',
    'Kerala': 'malayalam',
    'Andhra Pradesh': 'telugu',
    'Telangana': 'telugu',
    'Maharashtra': 'marathi',
    'Gujarat': 'gujarati',
    'Punjab': 'punjabi',
    'West Bengal': 'bengali',
    'Rajasthan': 'hindi',
    'Uttar Pradesh': 'hindi',
    'Bihar': 'hindi',
    'Madhya Pradesh': 'hindi',
    'Haryana': 'hindi',
    'Jharkhand': 'hindi',
    'Chhattisgarh': 'hindi',
    'Uttarakhand': 'hindi',
    'Himachal Pradesh': 'hindi',
    'Delhi': 'hindi',
    'Jammu and Kashmir': 'hindi',
    'Assam': 'assamese',
    'Odisha': 'odia',
    'Goa': 'konkani',
    'Arunachal Pradesh': 'english',
    'Manipur': 'english',
    'Meghalaya': 'english',
    'Mizoram': 'english',
    'Nagaland': 'english',
    'Sikkim': 'english',
    'Tripura': 'bengali',
    'Ladakh': 'hindi',
}

# Language display names
LANGUAGES = {
    'english': {'name': 'English', 'native': 'English'},
    'hindi': {'name': 'Hindi', 'native': 'हिंदी'},
    'tamil': {'name': 'Tamil', 'native': 'தமிழ்'},
    'telugu': {'name': 'Telugu', 'native': 'తెలుగు'},
    'kannada': {'name': 'Kannada', 'native': 'ಕನ್ನಡ'},
    'malayalam': {'name': 'Malayalam', 'native': 'മലയാളം'},
    'marathi': {'name': 'Marathi', 'native': 'मराठी'},
    'bengali': {'name': 'Bengali', 'native': 'বাংলা'},
    'gujarati': {'name': 'Gujarati', 'native': 'ગુજરાતી'},
    'punjabi': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ'},
    'odia': {'name': 'Odia', 'native': 'ଓଡ଼ିଆ'},
    'assamese': {'name': 'Assamese', 'native': 'অসমীয়া'},
    'konkani': {'name': 'Konkani', 'native': 'कोंकणी'},
}

# Complete Indian States with Districts - ALL 31 States and UTs
INDIAN_STATES_DISTRICTS = {
    'Andhra Pradesh': {
        'climate': 'Tropical, hot and humid',
        'major_crops': ['rice', 'cotton', 'sugarcane', 'tobacco', 'pulses'],
        'soil_types': ['red', 'black', 'alluvial'],
        'rainfall': '900-1200mm',
        'districts': ['Anantapur', 'Chittoor', 'East Godavari', 'Guntur', 'Krishna', 'Kurnool', 'Prakasam', 'Srikakulam', 'Visakhapatnam', 'Vizianagaram', 'West Godavari', 'YSR Kadapa', 'Nellore']
    },
    'Arunachal Pradesh': {
        'climate': 'Subtropical to alpine',
        'major_crops': ['rice', 'maize', 'millet', 'wheat', 'pulses'],
        'soil_types': ['alluvial', 'red'],
        'rainfall': '2000-4000mm',
        'districts': ['Tawang', 'West Kameng', 'East Kameng', 'Papum Pare', 'Kurung Kumey', 'Kra Daadi', 'Lower Subansiri', 'Upper Subansiri', 'West Siang', 'East Siang', 'Siang', 'Upper Siang', 'Lower Siang', 'Lower Dibang Valley', 'Dibang Valley', 'Anjaw', 'Lohit', 'Namsai', 'Changlang', 'Tirap', 'Longding']
    },
    'Assam': {
        'climate': 'Subtropical with high rainfall',
        'major_crops': ['rice', 'tea', 'jute', 'pulses', 'oilseeds'],
        'soil_types': ['alluvial', 'red'],
        'rainfall': '2000-3000mm',
        'districts': ['Baksa', 'Barpeta', 'Biswanath', 'Bongaigaon', 'Cachar', 'Charaideo', 'Chirang', 'Darrang', 'Dhemaji', 'Dhubri', 'Dibrugarh', 'Dima Hasao', 'Goalpara', 'Golaghat', 'Hailakandi', 'Hojai', 'Jorhat', 'Kamrup', 'Kamrup Metropolitan', 'Karbi Anglong', 'Karimganj', 'Kokrajhar', 'Lakhimpur', 'Majuli', 'Morigaon', 'Nagaon', 'Nalbari', 'Sivasagar', 'Sonitpur', 'South Salmara-Mankachar', 'Tinsukia', 'Udalguri', 'West Karbi Anglong']
    },
    'Bihar': {
        'climate': 'Subtropical',
        'major_crops': ['rice', 'wheat', 'maize', 'pulses', 'sugarcane'],
        'soil_types': ['alluvial'],
        'rainfall': '1000-1400mm',
        'districts': ['Araria', 'Arwal', 'Aurangabad', 'Banka', 'Begusarai', 'Bhagalpur', 'Bhojpur', 'Buxar', 'Darbhanga', 'East Champaran', 'Gaya', 'Gopalganj', 'Jamui', 'Jehanabad', 'Kaimur', 'Katihar', 'Khagaria', 'Kishanganj', 'Lakhisarai', 'Madhepura', 'Madhubani', 'Munger', 'Muzaffarpur', 'Nalanda', 'Nawada', 'Patna', 'Purnia', 'Rohtas', 'Saharsa', 'Samastipur', 'Saran', 'Sheikhpura', 'Sheohar', 'Sitamarhi', 'Siwan', 'Supaul', 'Vaishali', 'West Champaran']
    },
    'Chhattisgarh': {
        'climate': 'Tropical',
        'major_crops': ['rice', 'maize', 'pulses', 'oilseeds', 'sugarcane'],
        'soil_types': ['red', 'black'],
        'rainfall': '1200-1600mm',
        'districts': ['Balod', 'Baloda Bazar', 'Balrampur', 'Bastar', 'Bemetara', 'Bijapur', 'Bilaspur', 'Dantewada', 'Dhamtari', 'Durg', 'Gariaband', 'Janjgir-Champa', 'Jashpur', 'Kabirdham', 'Kanker', 'Kondagaon', 'Korba', 'Koriya', 'Mahasamund', 'Mungeli', 'Narayanpur', 'Raigarh', 'Raipur', 'Rajnandgaon', 'Sukma', 'Surajpur', 'Surguja']
    },
    'Goa': {
        'climate': 'Tropical coastal',
        'major_crops': ['rice', 'cashew', 'coconut', 'areca nut', 'vegetables'],
        'soil_types': ['laterite', 'alluvial'],
        'rainfall': '2500-3000mm',
        'districts': ['North Goa', 'South Goa']
    },
    'Gujarat': {
        'climate': 'Semi-arid to arid',
        'major_crops': ['cotton', 'groundnut', 'tobacco', 'wheat', 'bajra'],
        'soil_types': ['black', 'alluvial', 'sandy'],
        'rainfall': '400-1000mm',
        'districts': ['Ahmedabad', 'Amreli', 'Anand', 'Aravalli', 'Banaskantha', 'Bharuch', 'Bhavnagar', 'Botad', 'Chhota Udaipur', 'Dahod', 'Dang', 'Devbhoomi Dwarka', 'Gandhinagar', 'Gir Somnath', 'Jamnagar', 'Junagadh', 'Kheda', 'Kutch', 'Mahisagar', 'Mehsana', 'Morbi', 'Narmada', 'Navsari', 'Panchmahal', 'Patan', 'Porbandar', 'Rajkot', 'Sabarkantha', 'Surat', 'Surendranagar', 'Tapi', 'Vadodara', 'Valsad']
    },
    'Haryana': {
        'climate': 'Semi-arid',
        'major_crops': ['wheat', 'rice', 'sugarcane', 'cotton', 'bajra'],
        'soil_types': ['alluvial', 'sandy'],
        'rainfall': '400-600mm',
        'districts': ['Ambala', 'Bhiwani', 'Charkhi Dadri', 'Faridabad', 'Fatehabad', 'Gurugram', 'Hisar', 'Jhajjar', 'Jind', 'Kaithal', 'Karnal', 'Kurukshetra', 'Mahendragarh', 'Nuh', 'Palwal', 'Panchkula', 'Panipat', 'Rewari', 'Rohtak', 'Sirsa', 'Sonipat', 'Yamunanagar']
    },
    'Himachal Pradesh': {
        'climate': 'Temperate to alpine',
        'major_crops': ['wheat', 'maize', 'rice', 'barley', 'apples'],
        'soil_types': ['alluvial', 'mountain'],
        'rainfall': '1000-2000mm',
        'districts': ['Bilaspur', 'Chamba', 'Hamirpur', 'Kangra', 'Kinnaur', 'Kullu', 'Lahaul and Spiti', 'Mandi', 'Shimla', 'Sirmaur', 'Solan', 'Una']
    },
    'Jharkhand': {
        'climate': 'Tropical to subtropical',
        'major_crops': ['rice', 'maize', 'pulses', 'oilseeds', 'vegetables'],
        'soil_types': ['red', 'laterite'],
        'rainfall': '1200-1600mm',
        'districts': ['Bokaro', 'Chatra', 'Deoghar', 'Dhanbad', 'Dumka', 'East Singhbhum', 'Garhwa', 'Giridih', 'Godda', 'Gumla', 'Hazaribagh', 'Jamtara', 'Khunti', 'Koderma', 'Latehar', 'Lohardaga', 'Pakur', 'Palamu', 'Ramgarh', 'Ranchi', 'Sahibganj', 'Seraikela-Kharsawan', 'Simdega', 'West Singhbhum']
    },
    'Karnataka': {
        'climate': 'Tropical to semi-arid',
        'major_crops': ['rice', 'ragi', 'jowar', 'cotton', 'sugarcane'],
        'soil_types': ['red', 'black', 'laterite'],
        'rainfall': '600-3000mm',
        'districts': ['Bagalkot', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban', 'Bidar', 'Chamarajanagar', 'Chikkaballapur', 'Chikkamagaluru', 'Chitradurga', 'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan', 'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal', 'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga', 'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura', 'Yadgir']
    },
    'Kerala': {
        'climate': 'Tropical humid',
        'major_crops': ['rice', 'coconut', 'rubber', 'spices', 'cashew'],
        'soil_types': ['laterite', 'alluvial', 'coastal'],
        'rainfall': '2500-3500mm',
        'districts': ['Alappuzha', 'Ernakulam', 'Idukki', 'Kannur', 'Kasaragod', 'Kollam', 'Kottayam', 'Kozhikode', 'Malappuram', 'Palakkad', 'Pathanamthitta', 'Thiruvananthapuram', 'Thrissur', 'Wayanad']
    },
    'Madhya Pradesh': {
        'climate': 'Tropical to subtropical',
        'major_crops': ['wheat', 'soybean', 'gram', 'rice', 'cotton'],
        'soil_types': ['black', 'red', 'alluvial'],
        'rainfall': '800-1600mm',
        'districts': ['Agar Malwa', 'Alirajpur', 'Anuppur', 'Ashoknagar', 'Balaghat', 'Barwani', 'Betul', 'Bhind', 'Bhopal', 'Burhanpur', 'Chhatarpur', 'Chhindwara', 'Damoh', 'Datia', 'Dewas', 'Dhar', 'Dindori', 'Guna', 'Gwalior', 'Harda', 'Hoshangabad', 'Indore', 'Jabalpur', 'Jhabua', 'Katni', 'Khandwa', 'Khargone', 'Mandla', 'Mandsaur', 'Morena', 'Narsinghpur', 'Neemuch', 'Niwari', 'Panna', 'Raisen', 'Rajgarh', 'Ratlam', 'Rewa', 'Sagar', 'Satna', 'Sehore', 'Seoni', 'Shahdol', 'Shajapur', 'Sheopur', 'Shivpuri', 'Sidhi', 'Singrauli', 'Tikamgarh', 'Ujjain', 'Umaria', 'Vidisha']
    },
    'Maharashtra': {
        'climate': 'Tropical to semi-arid',
        'major_crops': ['cotton', 'sugarcane', 'rice', 'wheat', 'pulses'],
        'soil_types': ['black', 'red', 'laterite'],
        'rainfall': '400-3000mm',
        'districts': ['Ahmednagar', 'Akola', 'Amravati', 'Aurangabad', 'Beed', 'Bhandara', 'Buldhana', 'Chandrapur', 'Dhule', 'Gadchiroli', 'Gondia', 'Hingoli', 'Jalgaon', 'Jalna', 'Kolhapur', 'Latur', 'Mumbai City', 'Mumbai Suburban', 'Nagpur', 'Nanded', 'Nandurbar', 'Nashik', 'Osmanabad', 'Palghar', 'Parbhani', 'Pune', 'Raigad', 'Ratnagiri', 'Sangli', 'Satara', 'Sindhudurg', 'Solapur', 'Thane', 'Wardha', 'Washim', 'Yavatmal']
    },
    'Manipur': {
        'climate': 'Subtropical to temperate',
        'major_crops': ['rice', 'maize', 'pulses', 'oilseeds', 'sugarcane'],
        'soil_types': ['red', 'alluvial'],
        'rainfall': '1500-2500mm',
        'districts': ['Bishnupur', 'Chandel', 'Churachandpur', 'Imphal East', 'Imphal West', 'Jiribam', 'Kakching', 'Kamjong', 'Kangpokpi', 'Noney', 'Pherzawl', 'Senapati', 'Tamenglong', 'Tengnoupal', 'Thoubal', 'Ukhrul']
    },
    'Meghalaya': {
        'climate': 'Subtropical with heavy rainfall',
        'major_crops': ['rice', 'maize', 'potato', 'pulses', 'pineapple'],
        'soil_types': ['red', 'laterite'],
        'rainfall': '2000-12000mm',
        'districts': ['East Garo Hills', 'East Jaintia Hills', 'East Khasi Hills', 'North Garo Hills', 'Ri Bhoi', 'South Garo Hills', 'South West Garo Hills', 'South West Khasi Hills', 'West Garo Hills', 'West Jaintia Hills', 'West Khasi Hills']
    },
    'Mizoram': {
        'climate': 'Subtropical',
        'major_crops': ['rice', 'maize', 'pulses', 'oilseeds', 'cotton'],
        'soil_types': ['red', 'laterite'],
        'rainfall': '2000-3000mm',
        'districts': ['Aizawl', 'Champhai', 'Kolasib', 'Lawngtlai', 'Lunglei', 'Mamit', 'Saiha', 'Serchhip']
    },
    'Nagaland': {
        'climate': 'Subtropical to temperate',
        'major_crops': ['rice', 'maize', 'millet', 'pulses', 'oilseeds'],
        'soil_types': ['red', 'laterite'],
        'rainfall': '2000-2500mm',
        'districts': ['Dimapur', 'Kiphire', 'Kohima', 'Longleng', 'Mokokchung', 'Mon', 'Peren', 'Phek', 'Tuensang', 'Wokha', 'Zunheboto']
    },
    'Odisha': {
        'climate': 'Tropical',
        'major_crops': ['rice', 'pulses', 'oilseeds', 'jute', 'sugarcane'],
        'soil_types': ['red', 'laterite', 'alluvial'],
        'rainfall': '1200-1600mm',
        'districts': ['Angul', 'Balangir', 'Balasore', 'Bargarh', 'Bhadrak', 'Boudh', 'Cuttack', 'Deogarh', 'Dhenkanal', 'Gajapati', 'Ganjam', 'Jagatsinghpur', 'Jajpur', 'Jharsuguda', 'Kalahandi', 'Kandhamal', 'Kendrapara', 'Kendujhar', 'Khordha', 'Koraput', 'Malkangiri', 'Mayurbhanj', 'Nabarangpur', 'Nayagarh', 'Nuapada', 'Puri', 'Rayagada', 'Sambalpur', 'Subarnapur', 'Sundargarh']
    },
    'Punjab': {
        'climate': 'Semi-arid to sub-humid',
        'major_crops': ['wheat', 'rice', 'cotton', 'sugarcane', 'maize'],
        'soil_types': ['alluvial'],
        'rainfall': '400-600mm',
        'districts': ['Amritsar', 'Barnala', 'Bathinda', 'Faridkot', 'Fatehgarh Sahib', 'Fazilka', 'Ferozepur', 'Gurdaspur', 'Hoshiarpur', 'Jalandhar', 'Kapurthala', 'Ludhiana', 'Mansa', 'Moga', 'Mohali', 'Muktsar', 'Pathankot', 'Patiala', 'Rupnagar', 'Sangrur', 'Shaheed Bhagat Singh Nagar', 'Tarn Taran']
    },
    'Rajasthan': {
        'climate': 'Arid to semi-arid',
        'major_crops': ['bajra', 'wheat', 'barley', 'pulses', 'mustard'],
        'soil_types': ['sandy', 'alluvial'],
        'rainfall': '100-600mm',
        'districts': ['Ajmer', 'Alwar', 'Banswara', 'Baran', 'Barmer', 'Bharatpur', 'Bhilwara', 'Bikaner', 'Bundi', 'Chittorgarh', 'Churu', 'Dausa', 'Dholpur', 'Dungarpur', 'Hanumangarh', 'Jaipur', 'Jaisalmer', 'Jalore', 'Jhalawar', 'Jhunjhunu', 'Jodhpur', 'Karauli', 'Kota', 'Nagaur', 'Pali', 'Pratapgarh', 'Rajsamand', 'Sawai Madhopur', 'Sikar', 'Sirohi', 'Sri Ganganagar', 'Tonk', 'Udaipur']
    },
    'Sikkim': {
        'climate': 'Temperate to alpine',
        'major_crops': ['maize', 'rice', 'wheat', 'barley', 'cardamom'],
        'soil_types': ['mountain', 'alluvial'],
        'rainfall': '2000-3500mm',
        'districts': ['East Sikkim', 'North Sikkim', 'South Sikkim', 'West Sikkim']
    },
    'Tamil Nadu': {
        'climate': 'Tropical',
        'major_crops': ['rice', 'sugarcane', 'cotton', 'groundnut', 'millets'],
        'soil_types': ['red', 'black', 'alluvial'],
        'rainfall': '900-1400mm',
        'districts': ['Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dharmapuri', 'Dindigul', 'Erode', 'Kallakurichi', 'Kanchipuram', 'Kanyakumari', 'Karur', 'Krishnagiri', 'Madurai', 'Mayiladuthurai', 'Nagapattinam', 'Namakkal', 'Nilgiris', 'Perambalur', 'Pudukkottai', 'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga', 'Tenkasi', 'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli', 'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur', 'Vellore', 'Viluppuram', 'Virudhunagar']
    },
    'Telangana': {
        'climate': 'Tropical',
        'major_crops': ['rice', 'cotton', 'maize', 'sugarcane', 'turmeric'],
        'soil_types': ['red', 'black'],
        'rainfall': '900-1200mm',
        'districts': ['Adilabad', 'Bhadradri Kothagudem', 'Hyderabad', 'Jagtial', 'Jangaon', 'Jayashankar', 'Jogulamba', 'Kamareddy', 'Karimnagar', 'Khammam', 'Kumuram Bheem', 'Mahabubabad', 'Mahbubnagar', 'Mancherial', 'Medak', 'Medchal', 'Nagarkurnool', 'Nalgonda', 'Nirmal', 'Nizamabad', 'Peddapalli', 'Rajanna Sircilla', 'Rangareddy', 'Sangareddy', 'Siddipet', 'Suryapet', 'Vikarabad', 'Wanaparthy', 'Warangal Rural', 'Warangal Urban', 'Yadadri Bhuvanagiri']
    },
    'Tripura': {
        'climate': 'Subtropical',
        'major_crops': ['rice', 'jute', 'tea', 'rubber', 'pineapple'],
        'soil_types': ['alluvial', 'laterite'],
        'rainfall': '2000-2500mm',
        'districts': ['Dhalai', 'Gomati', 'Khowai', 'North Tripura', 'Sepahijala', 'South Tripura', 'Unakoti', 'West Tripura']
    },
    'Uttar Pradesh': {
        'climate': 'Subtropical',
        'major_crops': ['wheat', 'rice', 'sugarcane', 'potato', 'pulses'],
        'soil_types': ['alluvial'],
        'rainfall': '600-1200mm',
        'districts': ['Agra', 'Aligarh', 'Prayagraj', 'Ambedkar Nagar', 'Amethi', 'Amroha', 'Auraiya', 'Azamgarh', 'Baghpat', 'Bahraich', 'Ballia', 'Balrampur', 'Banda', 'Barabanki', 'Bareilly', 'Basti', 'Bijnor', 'Budaun', 'Bulandshahr', 'Chandauli', 'Chitrakoot', 'Deoria', 'Etah', 'Etawah', 'Ayodhya', 'Farrukhabad', 'Fatehpur', 'Firozabad', 'Gautam Buddha Nagar', 'Ghaziabad', 'Ghazipur', 'Gonda', 'Gorakhpur', 'Hamirpur', 'Hapur', 'Hardoi', 'Hathras', 'Jalaun', 'Jaunpur', 'Jhansi', 'Kannauj', 'Kanpur Dehat', 'Kanpur Nagar', 'Kasganj', 'Kaushambi', 'Kheri', 'Kushinagar', 'Lalitpur', 'Lucknow', 'Maharajganj', 'Mahoba', 'Mainpuri', 'Mathura', 'Mau', 'Meerut', 'Mirzapur', 'Moradabad', 'Muzaffarnagar', 'Pilibhit', 'Pratapgarh', 'Raebareli', 'Rampur', 'Saharanpur', 'Sambhal', 'Sant Kabir Nagar', 'Shahjahanpur', 'Shamli', 'Shravasti', 'Siddharthnagar', 'Sitapur', 'Sonbhadra', 'Sultanpur', 'Unnao', 'Varanasi']
    },
    'Uttarakhand': {
        'climate': 'Temperate to alpine',
        'major_crops': ['rice', 'wheat', 'sugarcane', 'potato', 'pulses'],
        'soil_types': ['alluvial', 'mountain'],
        'rainfall': '1000-2000mm',
        'districts': ['Almora', 'Bageshwar', 'Chamoli', 'Champawat', 'Dehradun', 'Haridwar', 'Nainital', 'Pauri Garhwal', 'Pithoragarh', 'Rudraprayag', 'Tehri Garhwal', 'Udham Singh Nagar', 'Uttarkashi']
    },
    'West Bengal': {
        'climate': 'Tropical to subtropical',
        'major_crops': ['rice', 'jute', 'tea', 'potato', 'wheat'],
        'soil_types': ['alluvial', 'red', 'laterite'],
        'rainfall': '1500-2500mm',
        'districts': ['Alipurduar', 'Bankura', 'Birbhum', 'Cooch Behar', 'Dakshin Dinajpur', 'Darjeeling', 'Hooghly', 'Howrah', 'Jalpaiguri', 'Jhargram', 'Kalimpong', 'Kolkata', 'Malda', 'Murshidabad', 'Nadia', 'North 24 Parganas', 'Paschim Bardhaman', 'Paschim Medinipur', 'Purba Bardhaman', 'Purba Medinipur', 'Purulia', 'South 24 Parganas', 'Uttar Dinajpur']
    },
    'Delhi': {
        'climate': 'Semi-arid',
        'major_crops': ['wheat', 'vegetables', 'fruits', 'flowers'],
        'soil_types': ['alluvial'],
        'rainfall': '600-700mm',
        'districts': ['Central Delhi', 'East Delhi', 'New Delhi', 'North Delhi', 'North East Delhi', 'North West Delhi', 'Shahdara', 'South Delhi', 'South East Delhi', 'South West Delhi', 'West Delhi']
    },
    'Jammu and Kashmir': {
        'climate': 'Temperate to alpine',
        'major_crops': ['rice', 'wheat', 'maize', 'barley', 'apples'],
        'soil_types': ['alluvial', 'mountain'],
        'rainfall': '400-1500mm',
        'districts': ['Anantnag', 'Bandipora', 'Baramulla', 'Budgam', 'Doda', 'Ganderbal', 'Jammu', 'Kathua', 'Kishtwar', 'Kulgam', 'Kupwara', 'Poonch', 'Pulwama', 'Rajouri', 'Ramban', 'Reasi', 'Samba', 'Shopian', 'Srinagar', 'Udhampur']
    },
    'Ladakh': {
        'climate': 'Cold desert',
        'major_crops': ['barley', 'wheat', 'peas', 'apricot', 'apple'],
        'soil_types': ['mountain', 'desert'],
        'rainfall': '100-200mm',
        'districts': ['Kargil', 'Leh']
    }
}

# Soil database
SOIL_CROP_DB = {
    'sandy': {
        'primary': ['groundnut', 'millet', 'watermelon', 'pulses'],
        'secondary': ['maize', 'sunflower', 'cashew'],
        'characteristics': 'Well-drained, low water retention, low nutrients',
        'improvement': 'Add organic matter, mulching, frequent irrigation'
    },
    'clay': {
        'primary': ['rice', 'wheat', 'sugarcane', 'cotton'],
        'secondary': ['jute', 'soybean', 'lentil'],
        'characteristics': 'High water retention, nutrient-rich, poor drainage',
        'improvement': 'Add gypsum, organic matter, improve drainage'
    },
    'loam': {
        'primary': ['wheat', 'potato', 'vegetables', 'maize'],
        'secondary': ['pulses', 'oilseeds', 'sugarcane'],
        'characteristics': 'Balanced drainage and nutrients, ideal for most crops',
        'improvement': 'Maintain organic matter, crop rotation'
    },
    'red': {
        'primary': ['groundnut', 'cotton', 'pulses', 'millets'],
        'secondary': ['maize', 'oilseeds', 'tobacco'],
        'characteristics': 'Iron-rich, porous, low fertility',
        'improvement': 'Add lime, fertilizers, green manuring'
    },
    'black': {
        'primary': ['cotton', 'soybean', 'sorghum', 'wheat'],
        'secondary': ['sunflower', 'pulses', 'safflower'],
        'characteristics': 'Moisture retentive, rich in calcium and magnesium',
        'improvement': 'Proper drainage, avoid over-watering'
    },
    'alluvial': {
        'primary': ['rice', 'wheat', 'sugarcane', 'jute'],
        'secondary': ['maize', 'pulses', 'vegetables'],
        'characteristics': 'Fertile, well-drained, rich in potash',
        'improvement': 'Regular fertilization, crop rotation'
    },
    'laterite': {
        'primary': ['cashew', 'coconut', 'rubber', 'areca nut'],
        'secondary': ['tapioca', 'pulses', 'groundnut'],
        'characteristics': 'Acidic, poor in nutrients, good drainage',
        'improvement': 'Add lime, organic manure, mulching'
    },
    'mountain': {
        'primary': ['wheat', 'barley', 'potato', 'maize'],
        'secondary': ['pulses', 'oilseeds', 'vegetables'],
        'characteristics': 'Variable, often rocky, moderate fertility',
        'improvement': 'Terracing, erosion control, organic matter'
    }
}

# Seasonal crops
SEASONAL_CROPS = {
    'kharif': ['rice', 'maize', 'cotton', 'soybean', 'groundnut', 'bajra', 'jowar', 'tur', 'moong', 'urad'],
    'rabi': ['wheat', 'mustard', 'potato', 'chickpea', 'lentil', 'barley', 'peas', 'gram', 'onion'],
    'zaid': ['watermelon', 'cucumber', 'muskmelon', 'vegetables', 'fodder', 'bitter gourd', 'pumpkin'],
    'perennial': ['sugarcane', 'banana', 'coconut', 'areca nut', 'cashew', 'rubber', 'tea', 'coffee']
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/states', methods=['GET'])
def get_states():
    states_list = list(INDIAN_STATES_DISTRICTS.keys())
    districts_map = {state: data['districts'] for state, data in INDIAN_STATES_DISTRICTS.items()}
    
    return jsonify({
        'states': states_list,
        'districts': districts_map,
        'state_data': INDIAN_STATES_DISTRICTS,
        'languages': LANGUAGES,
        'state_language_map': STATE_LANGUAGE_MAP
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.form.to_dict()
        
        required_fields = ['soil_type', 'state', 'district']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        state = data.get('state', '')
        state_info = INDIAN_STATES_DISTRICTS.get(state, None)
        
        if not state_info:
            return jsonify({
                'error': f'Invalid state: {state}. Please select a valid Indian state.'
            }), 400
        
        language = data.get('language', 'english')
        
        rule_suggestions = get_rule_based_suggestions(data, state_info)
        prompt = build_enhanced_prompt(data, state_info, rule_suggestions, language)
        ai_response = get_ai_recommendation(prompt)
        
        if ai_response is None:
            return jsonify({
                'error': 'Failed to get AI recommendation. Using rule-based suggestions.',
                'rule_suggestions': rule_suggestions,
                'state_info': state_info
            }), 200
        
        parsed_response = parse_ai_response(ai_response)
        
        return jsonify({
            'success': True,
            'ai_recommendation': parsed_response,
            'rule_suggestions': rule_suggestions,
            'state_info': state_info,
            'inputs': sanitize_inputs(data),
            'language': language
        })
        
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e) if app.debug else None
        }), 500

def get_rule_based_suggestions(data: Dict, state_info: Dict) -> Dict:
    soil_type = data.get('soil_type', '').lower()
    season = data.get('season', '').lower()
    
    soil_data = SOIL_CROP_DB.get(soil_type, {})
    primary_crops = soil_data.get('primary', [])
    secondary_crops = soil_data.get('secondary', [])
    
    seasonal_crops = SEASONAL_CROPS.get(season, [])
    if seasonal_crops:
        primary_crops = [c for c in primary_crops if c in seasonal_crops or c in state_info['major_crops']]
        secondary_crops = [c for c in secondary_crops if c in seasonal_crops or c in state_info['major_crops']]
    
    state_crops = [c for c in state_info['major_crops'] if c not in primary_crops][:3]
    
    return {
        'primary_crops': primary_crops,
        'secondary_crops': secondary_crops,
        'state_specific_crops': state_crops,
        'soil_characteristics': soil_data.get('characteristics', 'N/A'),
        'soil_improvement': soil_data.get('improvement', 'N/A'),
        'season': season or 'Not specified',
        'state_climate': state_info['climate'],
        'state_rainfall': state_info['rainfall']
    }

def build_enhanced_prompt(data: Dict, state_info: Dict, rule_suggestions: Dict, language: str) -> str:
    language_instruction = ""
    if language != 'english':
        lang_name = LANGUAGES.get(language, {}).get('name', language)
        language_instruction = f"\n\nIMPORTANT: Provide ALL recommendations, explanations, and text content in {lang_name} language. The JSON structure should remain in English, but all values, descriptions, and text should be in {lang_name}."
    
    prompt = f"""You are an agricultural expert specializing in Indian farming practices.

STATE INFORMATION - {data.get('state', 'N/A')} / {data.get('district', 'N/A')}:
- Climate: {state_info['climate']}
- Average Rainfall: {state_info['rainfall']}
- Major Crops: {', '.join(state_info['major_crops'])}
- Common Soil Types: {', '.join(state_info['soil_types'])}

FARMER'S INPUT DATA:
- State: {data.get('state', 'Not specified')}
- District: {data.get('district', 'Not specified')}
- Soil Type: {data.get('soil_type', 'Not specified')}
- Season: {data.get('season', 'Not specified')}
- Farm Size: {data.get('farm_size', 'Not specified')} acres
- Irrigation: {data.get('irrigation', 'Not specified')}
- Budget: ₹{data.get('budget', 'Not specified')}
- Previous Crop: {data.get('previous_crop', 'Not specified')}

RULE-BASED ANALYSIS:
- Soil Characteristics: {rule_suggestions['soil_characteristics']}
- Soil Improvement Tips: {rule_suggestions['soil_improvement']}
- Primary Crops for Soil: {', '.join(rule_suggestions['primary_crops'])}
- State-Specific Crops: {', '.join(rule_suggestions['state_specific_crops'])}

{language_instruction}

TASK: Provide detailed crop recommendations in the following EXACT JSON structure:

{{
  "recommended_crops": [
    {{
      "name": "Crop Name",
      "climate_suitability": "Explanation of why this crop suits the climate",
      "water_requirement": "Detailed water needs (e.g., 600-800mm, irrigation frequency)",
      "growth_cycle": {{
        "duration": "Total duration from sowing to harvest",
        "stages": "Key growth stages and their duration",
        "critical_periods": "When crop needs most attention"
      }},
      "benefits": {{
        "yield_potential": "Expected yield per acre",
        "market_demand": "Current market situation",
        "profitability": "Income potential and ROI",
        "nutritional_value": "If applicable",
        "other_benefits": "Soil improvement, short duration, etc."
      }},
      "cultivation_practices": {{
        "sowing_time": "Best time to sow",
        "seed_rate": "Seeds needed per acre",
        "spacing": "Row to row and plant to plant distance",
        "fertilizers": "NPK requirements and application schedule",
        "pest_diseases": "Common issues and prevention"
      }}
    }}
  ]
}}

Provide 3-5 most suitable crops. Respond ONLY with valid JSON, no additional text."""

    return prompt

def get_ai_recommendation(prompt: str, max_retries: int = 3) -> Optional[str]:
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 4096,
                }
            )
            
            if response and response.text:
                logger.info(f"Successfully received AI response on attempt {attempt + 1}")
                return response.text
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                logger.error("All retry attempts failed")
                return None
    
    return None

def parse_ai_response(response_text: str) -> Dict:
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            parsed = json.loads(json_str)
            return parsed
        else:
            return {'raw_response': response_text}
            
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {str(e)}")
        return {'raw_response': response_text}

def sanitize_inputs(data: Dict) -> Dict:
    return {k: v for k, v in data.items() if v and str(v).strip()}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'All India Crop Recommendation API',
        'states_covered': len(INDIAN_STATES_DISTRICTS),
        'gemini_configured': bool(GEMINI_KEY),
        'languages_supported': len(LANGUAGES)
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting All India Crop Recommendation System")
    logger.info(f"Covering {len(INDIAN_STATES_DISTRICTS)} states/UTs")
    logger.info(f"Supporting {len(LANGUAGES)} languages")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)