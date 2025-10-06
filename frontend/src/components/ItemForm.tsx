'use client';

import { useState } from 'react';
import { createItem, updateItem } from '@/app/lib/api';
import { Item } from '@/types';
import { useRouter } from 'next/navigation';

interface ItemFormProps {
    item?: Item;
    onSuccess?: () => void;
}

export default function ItemForm({ item, onSuccess }: ItemFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState(item?.title || '');
  const [description, setDescription] = useState(item?.description || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (item?.id) {
        await updateItem(item.id, { title, description });
      } else {
        await createItem({ title, description });
      }
      
      if (!item) {
        setTitle('');
        setDescription('');
      }
      
      router.refresh();
      
      if (onSuccess) onSuccess();
    } catch (err) {
      setError('Error saving item');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title"
          className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          required
        />
      </div>
      <div>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description"
          rows={3}
          className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
        />
      </div>
      <button 
        type="submit" 
        disabled={loading} 
        className="bg-blue-500 hover:bg-blue-600 text-white font-medium px-6 py-2.5 rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Saving...' : item ? 'Update Item' : 'Create Item'}
      </button>
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
    </form>
  );
}