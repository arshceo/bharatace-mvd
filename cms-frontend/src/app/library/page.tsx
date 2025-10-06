"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SidebarLayout from '@/components/SidebarLayout';
import { library as libraryApi } from '@/lib/api';
import { Plus, Search, Edit2, Trash2, Book, X } from 'lucide-react';

interface LibraryBook {
  id: string;
  title: string;
  author: string;
  isbn: string;
  category: string;
  quantity: number;
  available: number;
  publisher?: string;
  published_year?: number;
}

export default function LibraryPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [books, setBooks] = useState<LibraryBook[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedBook, setSelectedBook] = useState<LibraryBook | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    category: 'Computer Science',
    quantity: 1,
    publisher: '',
    published_year: new Date().getFullYear(),
  });

  useEffect(() => {
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
      router.push('/');
      return;
    }
    fetchBooks();
  }, [router]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const response = await libraryApi.getBooks();
      // Backend returns {books: [...]}
      const booksData = response.data.books || response.data || [];
      setBooks(Array.isArray(booksData) ? booksData : []);
    } catch (error) {
      console.error('Error fetching library books:', error);
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddBook = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await libraryApi.createBook({
        ...formData,
        available: formData.quantity,
      });
      setShowAddModal(false);
      fetchBooks();
      resetForm();
    } catch (error) {
      console.error('Error adding book:', error);
      alert('Failed to add book');
    }
  };

  const handleEditBook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBook) return;
    try {
      await libraryApi.updateBook(selectedBook.id, formData);
      setShowEditModal(false);
      fetchBooks();
      resetForm();
      setSelectedBook(null);
    } catch (error) {
      console.error('Error updating book:', error);
      alert('Failed to update book');
    }
  };

  const handleDeleteBook = async (id: string) => {
    if (!confirm('Are you sure you want to delete this book?')) return;
    try {
      await libraryApi.deleteBook(id);
      fetchBooks();
    } catch (error) {
      console.error('Error deleting book:', error);
      alert('Failed to delete book');
    }
  };

  const openEditModal = (book: LibraryBook) => {
    setSelectedBook(book);
    setFormData({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      category: book.category,
      quantity: book.quantity,
      publisher: book.publisher || '',
      published_year: book.published_year || new Date().getFullYear(),
    });
    setShowEditModal(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      author: '',
      isbn: '',
      category: 'Computer Science',
      quantity: 1,
      publisher: '',
      published_year: new Date().getFullYear(),
    });
  };

  const filteredBooks = Array.isArray(books) ? books.filter((book) => {
    const matchesSearch = 
      book?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      book?.author?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      book?.isbn?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'all' || book?.category === filterCategory;
    return matchesSearch && matchesCategory;
  }) : [];

  const categories = [
    'Computer Science', 'Software Engineering', 'Mathematics', 'Physics',
    'Chemistry', 'Electronics', 'Mechanical Engineering', 'Civil Engineering', 'Other'
  ];

  if (loading) {
    return (
      <SidebarLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        </div>
      </SidebarLayout>
    );
  }

  return (
    <SidebarLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Library Management</h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Total Books: {books.length} | Available: {books.reduce((sum, b) => sum + (b?.available || 0), 0)}
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Book
          </button>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search books..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
            </div>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Categories</option>
              {categories.map((category) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Book</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Author</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">ISBN</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Quantity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Available</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredBooks.map((book) => (
                  <tr key={book.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center">
                          <Book className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">{book.title}</div>
                          {book.publisher && (
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {book.publisher} ({book.published_year})
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{book.author}</td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{book.isbn}</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        {book.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{book.quantity}</td>
                    <td className="px-6 py-4">
                      <span className={`text-sm font-medium ${book.available > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {book.available}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => openEditModal(book)} className="text-indigo-600 hover:text-indigo-900 mr-4">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDeleteBook(book.id)} className="text-red-600 hover:text-red-900">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredBooks.length === 0 && (
              <div className="text-center py-12">
                <Book className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No books in library</h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Get started by adding a new book</p>
              </div>
            )}
          </div>
        </div>

        {(showAddModal || showEditModal) && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {showAddModal ? 'Add Book' : 'Edit Book'}
                  </h2>
                  <button 
                    onClick={() => { 
                      setShowAddModal(false); 
                      setShowEditModal(false); 
                      resetForm(); 
                      setSelectedBook(null);
                    }}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                <form onSubmit={showAddModal ? handleAddBook : handleEditBook} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Book Title *</label>
                      <input
                        type="text"
                        required
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Author *</label>
                      <input
                        type="text"
                        required
                        value={formData.author}
                        onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ISBN *</label>
                      <input
                        type="text"
                        required
                        value={formData.isbn}
                        onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category *</label>
                      <select
                        required
                        value={formData.category}
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        {categories.map((cat) => (
                          <option key={cat} value={cat}>{cat}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Quantity *</label>
                      <input
                        type="number"
                        required
                        min="1"
                        value={formData.quantity}
                        onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Publisher</label>
                      <input
                        type="text"
                        value={formData.publisher}
                        onChange={(e) => setFormData({ ...formData, publisher: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Year</label>
                      <input
                        type="number"
                        min="1900"
                        max={new Date().getFullYear()}
                        value={formData.published_year}
                        onChange={(e) => setFormData({ ...formData, published_year: parseInt(e.target.value) })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end space-x-3 mt-6">
                    <button
                      type="button"
                      onClick={() => { 
                        setShowAddModal(false); 
                        setShowEditModal(false); 
                        resetForm(); 
                        setSelectedBook(null);
                      }}
                      className="px-4 py-2 border rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                    >
                      {showAddModal ? 'Add Book' : 'Update Book'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </SidebarLayout>
  );
}
