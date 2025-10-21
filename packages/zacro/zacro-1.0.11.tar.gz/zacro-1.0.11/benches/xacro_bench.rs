use criterion::{criterion_group, criterion_main, Criterion};
use zacro::XacroProcessor;

fn benchmark_basic_macro_expansion(c: &mut Criterion) {
    c.bench_function("basic_macro_expansion", |b| {
        b.iter(|| {
            // TODO: Add actual benchmark code
            let _processor = XacroProcessor::new();
        });
    });
}

criterion_group!(benches, benchmark_basic_macro_expansion);
criterion_main!(benches);
