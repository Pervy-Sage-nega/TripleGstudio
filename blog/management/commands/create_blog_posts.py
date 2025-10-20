from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from blog.models import BlogPost, Category, Tag, BlogImage
import os
import shutil
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Create blog posts from blog data'

    def handle(self, *args, **options):
        # Get site manager user
        try:
            author = User.objects.get(email='rideouts200221@gmail.com')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Site manager not found'))
            return

        # Create categories
        categories = {
            'Architecture': Category.objects.get_or_create(
                name='Architecture',
                defaults={'description': 'Architectural designs and concepts', 'color': '#3498db'}
            )[0],
            'Interior Design': Category.objects.get_or_create(
                name='Interior Design', 
                defaults={'description': 'Interior design projects', 'color': '#e74c3c'}
            )[0],
            'Construction': Category.objects.get_or_create(
                name='Construction',
                defaults={'description': 'Construction projects and techniques', 'color': '#f39c12'}
            )[0],
            'Urban Planning': Category.objects.get_or_create(
                name='Urban Planning',
                defaults={'description': 'Urban development and planning', 'color': '#2ecc71'}
            )[0],
        }

        # Blog data
        blog_data = [
            {
                'title': 'Beauty Salon: Modern Elegance in Commercial Design',
                'folder': 'Beauty Salon',
                'category': categories['Interior Design'],
                'content': '''<h2>Transforming Beauty Through Design</h2>
                <p>Our latest beauty salon project showcases the perfect blend of functionality and aesthetic appeal. This modern commercial space was designed to create a luxurious yet welcoming environment for clients seeking beauty and wellness services.</p>
                
                <h3>Design Philosophy</h3>
                <p>The design philosophy centered around creating a serene, spa-like atmosphere while maintaining the efficiency required for a busy commercial salon. Clean lines, neutral tones, and strategic lighting work together to enhance the overall client experience.</p>
                
                <h3>Key Features</h3>
                <ul>
                <li>Open-concept layout maximizing natural light</li>
                <li>Premium materials including marble and brushed steel</li>
                <li>State-of-the-art ventilation and lighting systems</li>
                <li>Ergonomic workstations for staff comfort</li>
                <li>Dedicated relaxation areas for clients</li>
                </ul>
                
                <p>This project demonstrates our commitment to creating spaces that not only look beautiful but also enhance the functionality and success of our clients' businesses.</p>''',
                'excerpt': 'A modern beauty salon design that combines luxury aesthetics with practical functionality for an enhanced client experience.',
                'tags': ['beauty salon', 'commercial design', 'interior design', 'modern architecture']
            },
            {
                'title': 'Japanese Village: Harmony Between Tradition and Modernity',
                'folder': 'Japanese Village',
                'category': categories['Architecture'],
                'content': '''<h2>Embracing Japanese Design Principles</h2>
                <p>This residential project draws inspiration from traditional Japanese village architecture while incorporating modern living requirements. The design emphasizes harmony with nature, simplicity, and the thoughtful use of natural materials.</p>
                
                <h3>Traditional Elements</h3>
                <p>The project incorporates classic Japanese design elements including:</p>
                <ul>
                <li>Natural wood construction with exposed beams</li>
                <li>Sliding shoji screens for flexible space division</li>
                <li>Tatami-inspired flooring materials</li>
                <li>Zen garden integration</li>
                <li>Emphasis on natural light and ventilation</li>
                </ul>
                
                <h3>Modern Adaptations</h3>
                <p>While respecting traditional aesthetics, the design incorporates contemporary amenities and building techniques to meet modern lifestyle needs. The result is a harmonious blend that honors the past while embracing the future.</p>
                
                <p>This project showcases our ability to work with diverse cultural design traditions while creating spaces that are both authentic and functional for contemporary living.</p>''',
                'excerpt': 'A residential project that beautifully merges traditional Japanese village architecture with modern living requirements.',
                'tags': ['japanese architecture', 'traditional design', 'residential', 'cultural architecture']
            },
            {
                'title': 'Crystalline Reckonings: Geometric Precision in Modern Architecture',
                'folder': 'Crystalline Reckonings',
                'category': categories['Architecture'],
                'content': '''<h2>Geometric Innovation in Design</h2>
                <p>Crystalline Reckonings represents a bold exploration of geometric forms in contemporary architecture. This project pushes the boundaries of traditional design through the use of angular geometries and crystalline structures that create a striking visual impact.</p>
                
                <h3>Design Concept</h3>
                <p>The concept draws inspiration from natural crystal formations, translating their precise geometric patterns into architectural form. The building's facade features a series of interconnected angular panels that create dynamic shadows and reflections throughout the day.</p>
                
                <h3>Technical Innovation</h3>
                <p>The project required advanced engineering solutions to achieve the complex geometric forms while maintaining structural integrity. Key innovations include:</p>
                <ul>
                <li>Custom-fabricated angular panels</li>
                <li>Advanced structural support systems</li>
                <li>Integrated lighting design</li>
                <li>Climate-responsive facade elements</li>
                </ul>
                
                <p>This project demonstrates our expertise in pushing architectural boundaries while maintaining practical functionality and structural soundness.</p>''',
                'excerpt': 'An innovative architectural project featuring geometric precision and crystalline forms that challenge traditional design boundaries.',
                'tags': ['geometric design', 'modern architecture', 'innovative construction', 'facade design']
            },
            {
                'title': 'Dynamic Urban Continuum: Reshaping City Landscapes',
                'folder': 'Dynamic Urban Continuum',
                'category': categories['Urban Planning'],
                'content': '''<h2>Urban Development for the Future</h2>
                <p>The Dynamic Urban Continuum project represents a comprehensive approach to urban development that addresses the evolving needs of modern cities. This mixed-use development creates a seamless integration of residential, commercial, and public spaces.</p>
                
                <h3>Urban Integration</h3>
                <p>The project focuses on creating connections between different urban zones while maintaining distinct character areas. The design promotes walkability, sustainability, and community interaction through thoughtful planning and design.</p>
                
                <h3>Sustainable Features</h3>
                <ul>
                <li>Green building technologies throughout</li>
                <li>Integrated public transportation access</li>
                <li>Urban green spaces and parks</li>
                <li>Stormwater management systems</li>
                <li>Energy-efficient building systems</li>
                </ul>
                
                <h3>Community Impact</h3>
                <p>The development prioritizes community needs by providing diverse housing options, commercial opportunities, and public amenities that serve residents of all ages and backgrounds.</p>
                
                <p>This project showcases our commitment to creating urban environments that are not only functional but also enhance the quality of life for all residents.</p>''',
                'excerpt': 'A comprehensive urban development project that integrates residential, commercial, and public spaces for sustainable city living.',
                'tags': ['urban planning', 'mixed-use development', 'sustainable design', 'community development']
            },
            {
                'title': 'Payo ad Apfu: Cultural Heritage in Contemporary Design',
                'folder': 'Payo ad Apfu',
                'category': categories['Architecture'],
                'content': '''<h2>Honoring Cultural Heritage</h2>
                <p>The Payo ad Apfu project represents a thoughtful approach to incorporating cultural heritage elements into contemporary architectural design. This project demonstrates how traditional cultural values can be expressed through modern building techniques and materials.</p>
                
                <h3>Cultural Integration</h3>
                <p>The design process involved extensive research into local cultural traditions and architectural heritage. Key cultural elements were identified and reinterpreted for contemporary use while maintaining their symbolic and functional significance.</p>
                
                <h3>Design Elements</h3>
                <ul>
                <li>Traditional spatial arrangements adapted for modern use</li>
                <li>Local materials sourced from regional suppliers</li>
                <li>Cultural symbols integrated into architectural details</li>
                <li>Community gathering spaces reflecting traditional practices</li>
                <li>Sustainable building practices honoring environmental traditions</li>
                </ul>
                
                <h3>Community Engagement</h3>
                <p>The project involved extensive community consultation to ensure that the design authentically represents local cultural values while meeting contemporary functional requirements.</p>
                
                <p>This project exemplifies our commitment to culturally sensitive design that honors heritage while embracing innovation.</p>''',
                'excerpt': 'A culturally sensitive architectural project that honors local heritage while incorporating contemporary design principles.',
                'tags': ['cultural architecture', 'heritage design', 'community engagement', 'traditional materials']
            },
            {
                'title': 'Pellucid Reverence: Transparency in Modern Architecture',
                'folder': 'Pellucid Reverence',
                'category': categories['Architecture'],
                'content': '''<h2>The Art of Architectural Transparency</h2>
                <p>Pellucid Reverence explores the concept of transparency in modern architecture, creating spaces that blur the boundaries between interior and exterior environments. This project demonstrates how glass and light can be used to create ethereal, almost spiritual architectural experiences.</p>
                
                <h3>Design Philosophy</h3>
                <p>The design philosophy centers on the idea that architecture should enhance rather than obstruct the natural environment. Through the strategic use of transparent and translucent materials, the building creates a sense of lightness and connection with its surroundings.</p>
                
                <h3>Technical Achievements</h3>
                <ul>
                <li>Advanced glazing systems for optimal transparency</li>
                <li>Structural glass elements reducing visual barriers</li>
                <li>Integrated lighting design enhancing transparency effects</li>
                <li>Climate control systems maintaining comfort in glass environments</li>
                <li>Privacy solutions using smart glass technology</li>
                </ul>
                
                <h3>Environmental Considerations</h3>
                <p>Despite the extensive use of glass, the project maintains high energy efficiency through advanced glazing technologies and passive design strategies that work with natural light and ventilation patterns.</p>
                
                <p>This project showcases our expertise in creating architecturally striking buildings that maintain practical functionality and environmental responsibility.</p>''',
                'excerpt': 'An architectural exploration of transparency and light, creating ethereal spaces that connect interior and exterior environments.',
                'tags': ['transparent architecture', 'glass design', 'natural light', 'modern construction']
            },
            {
                'title': 'Shelas Ukay: Sustainable Community Development',
                'folder': 'Shelas Ukay',
                'category': categories['Urban Planning'],
                'content': '''<h2>Building Sustainable Communities</h2>
                <p>Shelas Ukay represents a comprehensive approach to sustainable community development that prioritizes environmental responsibility, social equity, and economic viability. This project demonstrates how thoughtful planning can create thriving communities that benefit both residents and the broader environment.</p>
                
                <h3>Sustainability Framework</h3>
                <p>The project is built on a comprehensive sustainability framework that addresses multiple aspects of community development:</p>
                <ul>
                <li>Renewable energy systems throughout the community</li>
                <li>Water conservation and recycling systems</li>
                <li>Local food production and community gardens</li>
                <li>Waste reduction and recycling programs</li>
                <li>Native landscaping and biodiversity preservation</li>
                </ul>
                
                <h3>Social Infrastructure</h3>
                <p>The community design prioritizes social connections and community well-being through shared spaces, recreational facilities, and programs that bring residents together.</p>
                
                <h3>Economic Sustainability</h3>
                <p>The project includes provisions for local economic development, including spaces for small businesses, co-working facilities, and community enterprises that keep economic benefits within the community.</p>
                
                <p>This project exemplifies our commitment to creating developments that are environmentally responsible, socially beneficial, and economically viable for the long term.</p>''',
                'excerpt': 'A comprehensive sustainable community development project that balances environmental responsibility with social and economic benefits.',
                'tags': ['sustainable development', 'community planning', 'green building', 'social infrastructure']
            },
            {
                'title': 'The Art of Transformation: Adaptive Reuse Excellence',
                'folder': 'The Art of Transformation',
                'category': categories['Architecture'],
                'content': '''<h2>Breathing New Life into Existing Structures</h2>
                <p>The Art of Transformation project showcases the potential of adaptive reuse in architecture. This project demonstrates how existing structures can be thoughtfully transformed to meet contemporary needs while preserving their historical and architectural significance.</p>
                
                <h3>Before and After</h3>
                <p>The transformation process involved careful analysis of the existing structure's strengths and challenges. The original building's character was preserved while introducing modern amenities and functionality required for contemporary use.</p>
                
                <h3>Preservation Strategies</h3>
                <ul>
                <li>Structural assessment and reinforcement where needed</li>
                <li>Preservation of significant architectural features</li>
                <li>Integration of modern building systems</li>
                <li>Accessibility improvements throughout</li>
                <li>Energy efficiency upgrades</li>
                </ul>
                
                <h3>Sustainable Benefits</h3>
                <p>Adaptive reuse provides significant environmental benefits by reducing demolition waste, preserving embodied energy in existing structures, and minimizing the need for new construction materials.</p>
                
                <h3>Design Innovation</h3>
                <p>The project required creative solutions to integrate modern functionality within the constraints of the existing structure, resulting in innovative design approaches that enhance both form and function.</p>
                
                <p>This project demonstrates our expertise in adaptive reuse and our commitment to sustainable building practices that honor architectural heritage.</p>''',
                'excerpt': 'A masterful adaptive reuse project that transforms an existing structure while preserving its architectural heritage and character.',
                'tags': ['adaptive reuse', 'historic preservation', 'sustainable renovation', 'architectural transformation']
            },
            {
                'title': 'The Lasting City: Designing for Urban Resilience',
                'folder': 'The Lasting City',
                'category': categories['Urban Planning'],
                'content': '''<h2>Building Cities for the Future</h2>
                <p>The Lasting City project addresses the critical need for urban resilience in the face of climate change and evolving social needs. This comprehensive urban planning initiative demonstrates how cities can be designed to adapt and thrive over time.</p>
                
                <h3>Resilience Framework</h3>
                <p>The project is built on a resilience framework that addresses multiple urban challenges:</p>
                <ul>
                <li>Climate adaptation strategies</li>
                <li>Infrastructure redundancy and flexibility</li>
                <li>Social and economic diversity</li>
                <li>Environmental sustainability</li>
                <li>Community preparedness and response capabilities</li>
                </ul>
                
                <h3>Adaptive Infrastructure</h3>
                <p>The urban design incorporates flexible infrastructure systems that can adapt to changing needs and conditions over time. This includes modular building systems, adaptable transportation networks, and scalable utility systems.</p>
                
                <h3>Community Resilience</h3>
                <p>The project prioritizes community resilience through the creation of strong social networks, local economic opportunities, and community resources that support residents during both normal times and periods of stress.</p>
                
                <h3>Long-term Vision</h3>
                <p>The Lasting City represents a long-term vision for urban development that considers not just immediate needs but also the evolving challenges and opportunities that cities will face in the coming decades.</p>
                
                <p>This project showcases our commitment to creating urban environments that are not only functional today but will continue to serve communities well into the future.</p>''',
                'excerpt': 'A comprehensive urban planning project focused on creating resilient cities that can adapt and thrive in the face of future challenges.',
                'tags': ['urban resilience', 'climate adaptation', 'sustainable cities', 'future planning']
            },
            {
                'title': 'Unorthodox A-Frame: Reimagining Classic Architecture',
                'folder': 'Unorthodox A-Frame',
                'category': categories['Architecture'],
                'content': '''<h2>A Fresh Take on A-Frame Design</h2>
                <p>The Unorthodox A-Frame project reimagines the classic A-frame architectural style for contemporary living. This innovative design maintains the iconic triangular profile while incorporating modern materials, technologies, and spatial arrangements that enhance functionality and comfort.</p>
                
                <h3>Design Innovation</h3>
                <p>The project challenges traditional A-frame limitations through creative design solutions:</p>
                <ul>
                <li>Expanded interior volumes through strategic design modifications</li>
                <li>Modern materials that enhance both aesthetics and performance</li>
                <li>Innovative window placement maximizing natural light</li>
                <li>Flexible interior spaces that adapt to different uses</li>
                <li>Integration of contemporary building systems</li>
                </ul>
                
                <h3>Structural Efficiency</h3>
                <p>The A-frame structure provides inherent structural efficiency while the modern interpretation optimizes this efficiency through advanced engineering and material selection.</p>
                
                <h3>Environmental Integration</h3>
                <p>The design emphasizes connection with the natural environment through strategic placement, material selection, and design elements that complement rather than compete with the surrounding landscape.</p>
                
                <h3>Contemporary Living</h3>
                <p>While honoring the A-frame tradition, the design fully accommodates contemporary lifestyle needs including modern kitchens, comfortable living spaces, and integrated technology systems.</p>
                
                <p>This project demonstrates our ability to honor architectural traditions while pushing boundaries to create innovative solutions for contemporary living.</p>''',
                'excerpt': 'An innovative reimagining of the classic A-frame design that combines traditional aesthetics with contemporary functionality.',
                'tags': ['a-frame architecture', 'modern residential', 'innovative design', 'structural efficiency']
            }
        ]

        # Create blog posts
        for blog_info in blog_data:
            # Check if blog post already exists
            if BlogPost.objects.filter(title=blog_info['title']).exists():
                self.stdout.write(f'Blog post already exists: {blog_info["title"]}')
                continue

            # Create blog post
            blog_post = BlogPost.objects.create(
                title=blog_info['title'],
                content=blog_info['content'],
                excerpt=blog_info['excerpt'],
                author=author,
                category=blog_info['category'],
                status='published',
                featured=True,
            )

            # Add tags
            for tag_name in blog_info['tags']:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                blog_post.tags.add(tag)

            # Copy images
            blog_folder = f'd:\\tripleG\\blogs\\{blog_info["folder"]}'
            if os.path.exists(blog_folder):
                # Set featured image (first image)
                images = [f for f in os.listdir(blog_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if images:
                    first_image = images[0]
                    src_path = os.path.join(blog_folder, first_image)
                    
                    # Copy to media directory
                    media_dir = 'd:\\tripleG\\TripleG\\media\\blog\\featured_images'
                    os.makedirs(media_dir, exist_ok=True)
                    
                    dest_filename = f"{blog_post.slug}_{first_image}"
                    dest_path = os.path.join(media_dir, dest_filename)
                    
                    if not os.path.exists(dest_path):
                        shutil.copy2(src_path, dest_path)
                    
                    # Update blog post
                    blog_post.featured_image = f'blog/featured_images/{dest_filename}'
                    blog_post.save()

                    # Add remaining images as gallery images
                    for i, img_name in enumerate(images[1:], 1):
                        src_path = os.path.join(blog_folder, img_name)
                        gallery_dir = 'd:\\tripleG\\TripleG\\media\\blog\\gallery'
                        os.makedirs(gallery_dir, exist_ok=True)
                        
                        gallery_filename = f"{blog_post.slug}_gallery_{i}_{img_name}"
                        gallery_dest = os.path.join(gallery_dir, gallery_filename)
                        
                        if not os.path.exists(gallery_dest):
                            shutil.copy2(src_path, gallery_dest)
                        
                        BlogImage.objects.create(
                            blog_post=blog_post,
                            image=f'blog/gallery/{gallery_filename}',
                            caption=f'Gallery image {i} for {blog_post.title}',
                            alt_text=f'{blog_post.title} - Image {i}',
                            order=i
                        )

            self.stdout.write(f'Created blog post: {blog_post.title}')

        self.stdout.write(self.style.SUCCESS('Successfully created all blog posts!'))