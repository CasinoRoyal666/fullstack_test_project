'use client';

import { useState, useEffect } from 'react';
import { getItems } from '@/app/lib/api';
import { Item } from '@/types';
import Link from 'next/link';

export default function ItemList() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const data = await getItems();
        setItems(data);
      } catch (err) {
        setError('Error fetching items');
      } finally {
        setLoading(false);
      }
    };
    fetchItems();
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <ul className="list-disc">
      {items.map((item) => (
        <li key={item.id}>
          <Link href={`/items/${item.id}`} className="text-blue-500">
            {item.title} ({item.created_at})
          </Link>
        </li>
      ))}
    </ul>
  );
}