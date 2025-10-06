import ItemForm from '@/components/ItemForm';
import { getItem, deleteItem } from '@/app/lib/api';
import { Item } from '@/types';
import { redirect } from 'next/navigation';

interface Params {
  params: { id: string };
}

export default async function ItemPage({ params }: Params) {
  const id = parseInt(params.id);
  let item: Item | null = null;
  try {
    item = await getItem(id);
  } catch {
    return <p>Item not found</p>;
  }

  async function handleDelete() {
    'use server';
    await deleteItem(id);
    redirect('/');
  }

  async function handleSuccess() {
    'use server';
    redirect('/');
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Item Details</h1>
      <ItemForm item={item} onSuccess={handleSuccess} />
      
      {}
      <form action={handleDelete}>
        <button type="submit" className="bg-red-500 text-white p-2 mt-4">
          Delete
        </button>
      </form>
    </div>
  );
}