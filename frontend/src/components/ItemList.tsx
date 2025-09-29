import { getItems } from '@/lib/api';
import { Item } from '@/types';
import Link from 'next/link';

export default async function ItemList() {
  let items: Item[] = [];
  let error: string | null = null;

  try {
    items = await getItems();
  } catch (err) {
    error = 'Error fetching items';
  }

  if (error) return <p className="text-red-500">{error}</p>;

  if (items.length === 0) {
    return <p className="text-gray-500">No items yet. Create one above!</p>;
  }

  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item.id} className="flex items-center">
          <Link
            href={`/items/${item.id}`}
            className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
          >
            {item.title}
          </Link>
          <span className="text-gray-400 text-sm ml-3">
            {new Date(item.created_at).toLocaleDateString()}
          </span>
        </li>
      ))}
    </ul>
  );
}
