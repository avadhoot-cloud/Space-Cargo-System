// frontend/src/components/Container3D.jsx

import React, { useRef, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Box, Text } from '@react-three/drei';
import * as THREE from 'three';

// Item component that represents an item in a container
const Item = ({ item, color = 'blue' }) => {
  // Calculate position based on the item's coordinates
  const position = [
    item.x_cm / 100 + item.width_cm / 200, 
    item.y_cm / 100 + item.height_cm / 200, 
    item.z_cm / 100 + item.depth_cm / 200
  ];
  
  // Calculate size based on the item's dimensions
  const size = [item.width_cm / 100, item.height_cm / 100, item.depth_cm / 100];
  
  // Determine color based on item properties (priority or sensitivity)
  let itemColor = color;
  if (item.sensitive === 'Yes' || item.sensitive === true || item.sensitive === 1) {
    itemColor = 'red';
  } else if (item.priority >= 80) {
    itemColor = 'orange';
  } else if (item.priority >= 50) {
    itemColor = 'yellow';
  }
  
  return (
    <>
      <Box position={position} args={size}>
        <meshStandardMaterial color={itemColor} transparent opacity={0.8} />
      </Box>
      <Text 
        position={[position[0], position[1] + size[1]/2 + 0.05, position[2]]}
        fontSize={0.05}
        color="white"
        anchorX="center"
        anchorY="bottom"
      >
        {item.item_id}
      </Text>
    </>
  );
};

// Container component that represents a container with items
const Container = ({ container, items }) => {
  // Calculate container dimensions
  const width = container.width_cm / 100;
  const height = container.height_cm / 100;
  const depth = container.depth_cm / 100;
  
  return (
    <group>
      {/* Container box */}
      <Box args={[width, height, depth]} position={[width/2, height/2, depth/2]}>
        <meshStandardMaterial color="gray" wireframe transparent opacity={0.3} />
      </Box>
      
      {/* Items inside container */}
      {items.map((item) => (
        <Item key={item.item_id} item={item} />
      ))}
    </group>
  );
};

// Rotating camera for better visualization
const RotatingCamera = () => {
  const cameraRef = useRef();
  const rotationSpeed = 0.0005;
  
  useFrame(({ clock }) => {
    if (cameraRef.current) {
      const t = clock.getElapsedTime();
      const x = Math.sin(t * rotationSpeed) * 5;
      const z = Math.cos(t * rotationSpeed) * 5;
      cameraRef.current.position.set(x, 3, z);
      cameraRef.current.lookAt(0, 0, 0);
    }
  });
  
  return null;
};

// Main Container3D component
const Container3D = ({ containerData, placedItems }) => {
  if (!containerData || !placedItems || placedItems.length === 0) {
    return (
      <div className="no-data-container">
        <p>No container or item data available for visualization</p>
      </div>
    );
  }
  
  return (
    <div className="container-3d" style={{ width: '100%', height: '400px' }}>
      <Canvas camera={{ position: [3, 3, 3], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <Container container={containerData} items={placedItems} />
        <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
        <gridHelper args={[10, 10]} />
        <axesHelper args={[3]} />
      </Canvas>
    </div>
  );
};

export default Container3D;