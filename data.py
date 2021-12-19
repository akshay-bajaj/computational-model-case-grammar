import random


class namesAndObjects:
    list_of_names = ["Aaradhya", "Adah", "Adhira", "Alisha", "Amoli", "Anaisha", "Ananya", "Anika", "Anushka", "Asmee",
                     "Avni", "Carina", "Drishti", "Hiya", "Ira", "Ishana", "Ishita", "Kaia", "Kashvi", "Keya", "Kimaya",
                     "Krisha", "Larisa", "Mahika", "Mayra", "Mehar", "Mirai", "Mishka", "Naitee", "Navya", "Nehrika",
                     "Neysa", "Pavati", "Prisha", "Ryka", "Rebecca", "Saanvi", "Sahana", "Sai", "Saisha", "Saloni",
                     "Shanaya", "Shrishti", "Sneha", "Taahira", "Taara", "Tanvi", "Viti", "Zara", "Aahva", "Aadiv",
                     "Aarav",
                     "Akanksh", "Alex", "Anant", "Atiksh", "Ayaan", "Bhuv", "Dasya", "Gian", "Hem", "Idhant", "Ishank",
                     "Jash", "Jay", "Joseph", "Kabir", "Kahaan", "Kairav", "Kevin", "Laksh", "Luv", "Manan", "Mohammad",
                     "Naksh", "Nimit", "Nirav", "Pahal", "Parv", "Pranay", "Rachit", "Raj", "Ranbir", "Raunak",
                     "Reyansh",
                     "Rishaan", "Rishit", "Rohan", "Rudra", "Rushil", "Sadhil", "Sarthak", "Taarush", "Taksh", "Ved",
                     "Vihaan", "Vivaan", "Yash", "Yug", "Zuber"]

    def random_name_generator(self, n):
        if len(self.list_of_names) >= n:
            names_generated = random.sample(self.list_of_names, n)
            return names_generated

    list_of_items = ["Pen", "Diary", "Bottle", "Glasses", "Watch", "Camera", "Brush", "Credit-Card", "Key",
                     "Mobile-Phone", "Wallet", "Umbrella", "Pencil", "Lighter", "Purse", "Scissors", "Passport",
                     "Comb", "Notebook", "Laptop", "Headphone", "Magazine"]

    def random_object_generator(self, n):
        names_generated = random.sample(self.list_of_items, n)
        return names_generated

    list_of_locations = ["Floor", "Table", "Desk", "Couch", "Mat", "Ground", "Chair"]

    def random_surface_generator(self, n):
        names_generated = random.sample(self.list_of_locations, n)
        return names_generated
