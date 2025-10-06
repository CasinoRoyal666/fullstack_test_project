'use client';

import { useState } from 'react';
import { createItem, updateItem } from '@/app/lib/api';
import { Item } from '@/types';

interface ItemFormProps {
    item?: Item; //If item is passed, then edit mode
    onSuccess?: () => void; //callback
}

export default function ItemForm({ item, onSuccess }: ItemFormProps) {
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
      if (onSuccess) onSuccess();
      setTitle('');
      setDescription('');
    } catch (err) {
      setError('Error saving item');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-8">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Title"
        className="border p-2 mr-2"
        required
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
        className="border p-2"
      />
      <button type="submit" disabled={loading} className="bg-blue-500 text-white p-2">
        {loading ? 'Saving...' : item ? 'Update' : 'Create'}
      </button>
      {error && <p className="text-red-500">{error}</p>}
    </form>
  );
}