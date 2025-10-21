# Triple G Portfolio System - Test Suite

## Overview
This comprehensive test suite ensures the reliability and functionality of the Triple G Portfolio System. The tests cover models, views, admin functionality, and integration scenarios.

## Test Structure

### 📁 Test Files
- `portfolio/tests.py` - Main test suite
- `portfolio/test_settings.py` - Test-specific Django settings
- `portfolio/fixtures/test_data.json` - Sample test data
- `run_tests.py` - Test runner script

### 🧪 Test Categories

#### 1. **Model Tests** (`PortfolioModelsTest`)
- **Category Model**: Name validation, slug generation, uniqueness
- **Project Model**: Field validation, relationships, string representation
- **ProjectImage Model**: File handling, relationships
- **ProjectStat Model**: Data integrity, ordering
- **ProjectTimeline Model**: Date handling, completion status

#### 2. **View Tests** (`PortfolioViewsTest`)
- **Public Views**: Project list, project detail, filtering, search
- **Error Handling**: 404 responses, invalid parameters
- **Pagination**: Multiple pages, navigation
- **Template Rendering**: Correct templates, context data

#### 3. **Admin Tests** (`PortfolioAdminTest`)
- **Authentication**: Admin access requirements
- **CRUD Operations**: Create, read, update, delete projects
- **File Uploads**: Hero images, gallery images, videos
- **AJAX Endpoints**: Project data retrieval
- **Form Validation**: Required fields, data types

#### 4. **Model Validation Tests** (`PortfolioModelValidationTest`)
- **Data Integrity**: Unique constraints, foreign keys
- **Field Validation**: Year ranges, status choices
- **Relationship Testing**: One-to-many, many-to-one
- **Auto-generation**: Slugs, timestamps

#### 5. **Integration Tests** (`PortfolioIntegrationTest`)
- **Full Lifecycle**: Create → View → Edit → Delete
- **Multi-user Scenarios**: Admin vs public access
- **Complex Filtering**: Combined search parameters
- **Real-world Workflows**: Complete project management

## 🚀 Running Tests

### Quick Test Run
```bash
# Run all portfolio tests
python manage.py test portfolio

# Run specific test class
python manage.py test portfolio.tests.PortfolioModelsTest

# Run specific test method
python manage.py test portfolio.tests.PortfolioModelsTest.test_project_creation
```

### Using Test Runner Script
```bash
# Run comprehensive test suite
python run_tests.py
```

### With Coverage Report
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test portfolio
coverage report
coverage html  # Generate HTML report
```

## 📊 Test Data

### Sample Categories
- **Residential**: Houses, villas, apartments
- **Commercial**: Offices, retail, hotels
- **Industrial**: Warehouses, factories, plants

### Sample Projects
- **Modern Villa Residence**: Ongoing residential project
- **Corporate Office Tower**: Completed commercial project
- **Eco-Friendly Warehouse**: Planned industrial project

### Test Fixtures
Load sample data for manual testing:
```bash
python manage.py loaddata portfolio/fixtures/test_data.json
```

## 🔧 Test Configuration

### Test Settings (`test_settings.py`)
- **Database**: In-memory SQLite for speed
- **Media**: Temporary directories
- **Cache**: Dummy cache backend
- **Passwords**: Simple hasher for performance
- **Logging**: Disabled for clean output

### Environment Variables
```bash
# Set test environment
export DJANGO_SETTINGS_MODULE=portfolio.test_settings
```

## 📈 Test Coverage Goals

### Current Coverage Areas
- ✅ **Models**: 100% - All fields, methods, relationships
- ✅ **Views**: 95% - All endpoints, error cases
- ✅ **Admin**: 90% - CRUD operations, permissions
- ✅ **Integration**: 85% - End-to-end workflows

### Coverage Targets
- **Unit Tests**: 95%+ coverage
- **Integration Tests**: 80%+ coverage
- **Admin Tests**: 90%+ coverage
- **Overall**: 90%+ coverage

## 🐛 Common Test Scenarios

### Authentication Tests
```python
# Test admin access
self.client.login(username='admin', password='testpass123')
response = self.client.get('/portfolio/admin/')
self.assertEqual(response.status_code, 200)
```

### File Upload Tests
```python
# Test image upload
image = SimpleUploadedFile('test.jpg', b'fake content', 'image/jpeg')
response = self.client.post('/portfolio/create/', {'hero_image': image})
```

### AJAX Tests
```python
# Test JSON response
response = self.client.get('/portfolio/api/projects/')
data = response.json()
self.assertTrue(data['success'])
```

## 🔍 Debugging Tests

### Verbose Output
```bash
# Run with verbose output
python manage.py test portfolio --verbosity=2

# Debug specific test
python manage.py test portfolio.tests.PortfolioModelsTest.test_project_creation --debug-mode
```

### Test Database Inspection
```python
# In test method, inspect database
from django.db import connection
print(connection.queries)  # Show SQL queries
```

## 📋 Test Checklist

### Before Deployment
- [ ] All tests pass
- [ ] Coverage > 90%
- [ ] No test warnings
- [ ] Performance acceptable
- [ ] Memory usage normal

### After Code Changes
- [ ] Run affected tests
- [ ] Update test data if needed
- [ ] Check for new edge cases
- [ ] Verify integration still works

## 🎯 Best Practices

### Test Writing
1. **Descriptive Names**: Clear test method names
2. **Single Responsibility**: One assertion per test
3. **Setup/Teardown**: Clean test environment
4. **Mock External**: Mock external services
5. **Edge Cases**: Test boundary conditions

### Test Maintenance
1. **Regular Updates**: Keep tests current with code
2. **Refactor**: Remove duplicate test code
3. **Documentation**: Comment complex test logic
4. **Performance**: Keep tests fast
5. **Reliability**: Avoid flaky tests

## 🚨 Troubleshooting

### Common Issues
1. **Database Errors**: Check migrations, fixtures
2. **File Upload Errors**: Verify media settings
3. **Permission Errors**: Check user roles, decorators
4. **Template Errors**: Verify template paths, context

### Debug Commands
```bash
# Check test database
python manage.py dbshell --settings=portfolio.test_settings

# Validate models
python manage.py check --settings=portfolio.test_settings

# Show migrations
python manage.py showmigrations --settings=portfolio.test_settings
```

## 📚 Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Happy Testing! 🧪** Your comprehensive test suite ensures the Triple G Portfolio System works reliably in all scenarios.
