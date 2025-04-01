import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from 'react-three-fiber';
import '../styles/ContainerGrid.css';

// A simple box to represent an item
const Item = ({ position, size, color }) => {
  return (
    <mesh position={position}>
      <boxGeometry args={size} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
};

// Container visualization component
const ContainerView = ({ container, items }) => {
  const containerRef = useRef();
  
  useFrame(() => {
    if (containerRef.current) {
      containerRef.current.rotation.y += 0.005;
    }
  });
  
  return (
    <group ref={containerRef}>
      {/* Container wireframe */}
      <mesh>
        <boxGeometry 
          args={[container.width, container.height, container.depth]} 
        />
        <meshStandardMaterial wireframe={true} color="white" />
      </mesh>
      
      {/* Items inside the container */}
      {items.map((item, index) => {
        // Calculate size based on volume (simplified as cube for visualization)
        const size = Math.cbrt(item.volume);
        const itemSize = [size, size, size];
        
        // Calculate position
        const position = [
          item.position_x - container.width/2 + size/2,
          item.position_y - container.height/2 + size/2,
          item.position_z - container.depth/2 + size/2
        ];
        
        // Generate a color based on item priority
        const colors = ['#3498db', '#2ecc71', '#f1c40f', '#e67e22', '#e74c3c'];
        const color = colors[Math.min(item.priority - 1, colors.length - 1)];
        
        return (
          <Item 
            key={index} 
            position={position} 
            size={itemSize} 
            color={color} 
          />
        );
      })}
    </group>
  );
};

const ContainerGrid = ({ container, items }) => {
  if (!container) {
    return <div className="container-grid empty">No container selected</div>;
  }
  
  return (
    <div className="container-grid">
      <h2>{container.name}</h2>
      <div className="container-info">
        <p>Dimensions: {container.width} × {container.height} × {container.depth}</p>
        <p>Weight: {container.current_weight} / {container.max_weight} kg</p>
        <p>Items: {items.length}</p>
      </div>
      
      <div className="container-visualization">
        <Canvas>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          <ContainerView container={container} items={items} />
        </Canvas>
      </div>
    </div>
  );
};

export default ContainerGrid; 