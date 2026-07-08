/**
 * Inicio — el pulso. Tres bandas: en caliente / para repasar / prep para hoy.
 * Slice 5 las llena con datos reales; aquí está la estructura con estados vacíos tranquilos.
 */

function Band({ title, hint }: { title: string; hint: string }) {
  return (
    <section className="mb-6">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-stone-500">{title}</h2>
      <div className="rounded-xl border border-dashed border-stone-300 p-4 text-sm text-stone-400">
        {hint}
      </div>
    </section>
  );
}

export default function Inicio() {
  return (
    <>
      <h1 className="mb-6 text-2xl font-bold">lengua</h1>
      <Band title="En caliente" hint="Los conceptos recién promovidos aparecerán aquí." />
      <Band title="Para repasar" hint="Tu repaso del día, cuando haya vocabulario que repasar." />
      <Band title="Prep para hoy" hint="Preparación para tus citas de hoy." />
      <p className="mt-10 text-center text-sm text-stone-400">
        Captura algo de tu día con el botón <span className="font-semibold text-amber-600">+</span>
      </p>
    </>
  );
}
