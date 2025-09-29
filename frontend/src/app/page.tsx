import ItemList from '@/components/ItemList';
import ItemForm from '@/components/ItemForm';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function Home() {
  return (
    <main className="space-y-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">Items List</h1>
        <ItemForm />
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <ItemList />
      </div>
    </main>
  );
}
