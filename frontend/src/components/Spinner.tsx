export default function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-slate-400 text-sm">
      <span className="inline-block w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      {label || "Working…"}
    </div>
  );
}
