from admin_panel.repository import CategoryRepository


class CategoryService:
    @staticmethod
    def get_all_categories():
        return CategoryRepository.get_all_categories()

    @staticmethod
    def get_category(category_id):
        return CategoryRepository.get_category(category_id)

    @staticmethod
    def create_category(data):
        return CategoryRepository.create_category(data)

    @staticmethod
    def update_category(category, data):
        return CategoryRepository.update_category(
            category,
            data,
        )

    @staticmethod
    def delete_category(category):
        CategoryRepository.delete_category(category)
